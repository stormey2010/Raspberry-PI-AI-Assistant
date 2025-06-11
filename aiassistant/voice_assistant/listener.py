# Imports
import pyaudio
import numpy as np
from openwakeword.model import Model
import argparse
import time
import wave
import asyncio
import os

# Import custom modules
from tts import fetch_tts_audio
from stt import stt
from llm import call_llm_api
from utils.volume import adjust_volume_by_time
from utils.play_audio import play_audio

# Directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Parse input arguments
parser=argparse.ArgumentParser()

parser.add_argument(
    "--chunk_size",
    help="How much audio (in number of samples) to predict on at once",
    type=int,
    default=1280,
    required=False
)
parser.add_argument(
    "--model_path",
    help="The path of a specific model to load",
    type=str,
    default=os.path.join(SCRIPT_DIR, "models", "Noh_vuh.tflite"),
    required=False
)
parser.add_argument(
    "--inference_framework",
    help="The inference framework to use (either 'onnx' or 'tflite'",
    type=str,
    default='tflite',
    required=False
)

parser.add_argument(
    "--trigger_threshold",
    help="Score threshold to detect wakeword",
    type=float,
    default=0.5,
    required=False
)

parser.add_argument(
    "--speech_threshold",
    help="Amplitude threshold for speech detection",
    type=int,
    default=2000,
    required=False
)

args = parser.parse_args()

# Get microphone stream
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = args.chunk_size
audio = pyaudio.PyAudio()
mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# Load pre-trained openwakeword models
if args.model_path != "":
    owwModel = Model(wakeword_models=[args.model_path], inference_framework=args.inference_framework)
else:
    owwModel = Model(inference_framework=args.inference_framework)

n_models = len(owwModel.models.keys())

# Define the lock file path consistently with api.py
TTS_PLAYING_LOCK_FILE = os.path.join(SCRIPT_DIR, "audio", "tts_playing.lock")

# Run capture loop continuosly, checking for wakewords
if __name__ == "__main__":
    threshold = args.trigger_threshold
    speech_threshold = args.speech_threshold
    print("wakeword started")
    while True:
        if os.path.exists(TTS_PLAYING_LOCK_FILE):
            time.sleep(0.1)  
            continue 

        # Grab one chunk and predict
        audio_data = np.frombuffer(
            mic_stream.read(CHUNK, exception_on_overflow=False),
            dtype=np.int16
        )
        prediction = owwModel.predict(audio_data)

        # Detect wakeword using adjustable threshold
        if prediction and any(score > threshold for score in prediction.values()):
            owwModel.reset()  # clear model state to prevent repeat triggers
            adjust_volume_by_time()

            print("wakeword detected")
            play_audio(os.path.join(SCRIPT_DIR, "audio", "start.wav"))

            # start collecting speech into buffer
            speech_buffer = []

            # listen for speech: timeout if no speech within 4 s, and stop when 0.7 s of silence
            start_time = time.time()
            last_speech_time = None
            while True:
                data = mic_stream.read(CHUNK, exception_on_overflow=False)
                speech_buffer.append(data)
                amplitude = np.max(np.abs(np.frombuffer(data, np.int16)))
                now = time.time()

                if amplitude >= speech_threshold:
                    last_speech_time = now

                if last_speech_time is None:
                    if now - start_time > 4.0:
                        print("no speech detected within 4 seconds, exiting")
                        break
                else:
                    if now - last_speech_time > 0.7:
                        break

            print("done speaking")
            play_audio(os.path.join(SCRIPT_DIR, "audio", "done.wav"))

            # write out the recorded speech (overwrite if exists)
            with wave.open(os.path.join(SCRIPT_DIR, 'audio', 'speech.wav'), 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(audio.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(speech_buffer))

            # run STT → LLM → TTS pipeline
            transcription = asyncio.run(stt())
            print(f"Transcription: {transcription}")

            reply, cont = asyncio.run(call_llm_api(transcription))
            print(f"LLM reply: {reply}")

            tts_path = asyncio.run(fetch_tts_audio(reply))
            if tts_path:
                print(f"TTS audio saved at: {tts_path}")
            os.system(f"aplay {os.path.join(SCRIPT_DIR, 'audio', tts_path)}")
            print("wakeword started")