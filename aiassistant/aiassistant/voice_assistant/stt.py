import os
from groq import Groq

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
client = Groq(api_key="YOUR_API_KEY")
filename = os.path.join(SCRIPT_DIR, "audio", "speech.wav")

async def stt():
    import asyncio
    def sync_stt():
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3-turbo",
                prompt="",
                response_format="verbose_json",
            )
            return transcription.text
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sync_stt)
