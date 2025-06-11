# Ai Assistant for Raspberry PI

## Prerequisites

- Python 3.11 or higher
- `pyaudio` for audio input/output
- `openwakeword` for wake word detection
- A Groq API key for speech-to-text
- Internet connection for API services

## Project Structure

```
aiassistant/
├── api/
│   ├── api.py           # API endpoints
│   └── test_api.py      # API tests
├── voice_assistant/
│   ├── listener.py      # Main wake word detection
│   ├── llm.py          # Language model integration
│   ├── stt.py          # Speech-to-text conversion
│   ├── tts.py          # Text-to-speech conversion
│   ├── audio/          # Audio resources
│   │   ├── done.wav
│   │   ├── error.wav
│   │   └── start.wav
│   ├── models/         # Wake word models
│   └── utils/          # Helper utilities
│       ├── play_audio.py
│       └── volume.py
```

## Setup Instructions

1. Clone this repository

2. Create a Python virtual environment (recommended):

   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies using the requirements file:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your API keys:

   - Create a Groq account and get your API key
   - Open `aiassistant/voice_assistant/stt.py`
   - Replace `YOUR_API_KEY` with your actual Groq API key

5. Set up LLM and TTS logic:
   - Open `aiassistant/voice_assistant/llm.py` and `aiassistant/voice_assistant/tts.py`
   - Add your llm api and tts api

## Train Your Own Wake Word

### 1. Think of a Wake Word

- Pick a short phrase or word (3–4 syllables) that’s not too common.
- Only **English** wake words are supported for now.

### 2. Open the Training Environment

Go to this [Colab notebook](https://colab.research.google.com/drive/1q1oe2zOyZp7UsB3jJiQ1IFn8z5YfjwEb?usp=sharing#scrollTo=1cbqBebHXjFD) to start training your wake word.

### 3. Enter Your Wake Word

In **Section 1**, fill in your wake word in the `target_word` field.

![Enter wake word](https://www.home-assistant.io/images/assist/wake_word_enter_target_word.png)

### 4. Run the Code

Click the ▶️ play button next to `target_word`.

> ⚠️ This step takes about 5-10 minutes on first run.

- If the play button doesn't show up, make sure your cursor is in that field.  
  ![Press play button](https://www.home-assistant.io/images/assist/wake_word_press_play_button.png)

- Still not working?
  - Look at the top-right of the notebook – it should say **Connected**.
  - If not, click **Connect to a hosted runtime**.  
    ![Connect to runtime](https://www.home-assistant.io/images/assist/wake_word_connect_to_hosted_runtime.png)

### Result: A Demo of Your Wake Word

Once it runs, you’ll see an audio file appear. Listen to the sample.

![Listen to demo](https://www.home-assistant.io/images/assist/wake_word_listen_demo.png)

### 5. Tweak It If It Sounds Off

- Change how it’s spelled so it sounds right when spoken.
- Run the play button again until it sounds correct.

### 6. Finalize Training

Once you're happy, go to **Runtime → Run all**.

![Run all](https://www.home-assistant.io/images/assist/wake_word_runtime_run_all.png)

> ⚠️ This step takes about an hour. Keep the browser tab open.

### Result:

After it finishes, you’ll get two files:

- `.tflite` (used)
- `.onnx` (not used)

### 7. Done!

You just trained your own wake word using **machine learning**!

### Using Your Wake Word

1. Copy your generated `.tflite` file to `aiassistant/voice_assistant/models/`
2. Update the wake word model path in `aiassistant/voice_assistant/listener.py`
3. Run the voice assistant:
   ```bash
   ./start.sh
   ```

## Troubleshooting

- If you get audio input/output errors:
  - Make sure your microphone is properly connected and set as default
  - Check if PyAudio is properly installed
- If the wake word isn't responding:
  - Try adjusting your speaking volume and distance from the microphone
  - Make sure you're pronouncing it similarly to how you trained it
  - Check if the correct model file is being loaded
