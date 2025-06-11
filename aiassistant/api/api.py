import sys
import os
# Set up project root directory for imports
project_root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root_dir not in sys.path:
    sys.path.insert(0, project_root_dir)

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import subprocess
import re
import uvicorn
from voice_assistant.tts import fetch_tts_audio  # Changed to absolute import
import os
import subprocess

# Configuration settings
AUDIO_DIR = os.path.join(project_root_dir, 'voice_assistant', 'audio')
LOCK_FILE_NAME = 'tts_playing.lock'

def get_lock_file_path():
    """Get the full path to the TTS lock file"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    return os.path.join(AUDIO_DIR, LOCK_FILE_NAME)

app = FastAPI(title="API")

@app.get("/volume")
def get_volume():
    try:
        # Get the current volume using amixer
        result = subprocess.check_output(["amixer", "get", "Master"]).decode()
        # Extract volume percentage from amixer output
        match = re.search(r"\[(\d{1,3})%\]", result)
        if match:
            return {"volume": int(match.group(1))}
        else:
            raise HTTPException(status_code=500, detail="Could not parse volume")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/volume/{level}")
def set_volume(level: int):
    # Ensure volume is within valid range
    if not (0 <= level <= 100):
        raise HTTPException(status_code=400, detail="Volume must be 0-100")
    try:
        # Set the system volume using amixer
        subprocess.run(["amixer", "set", "Master", f"{level}%"], check=True)
        return {"status": "success", "volume": level}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cpu_temp")
def cpu_temp():
    try:
        # Get CPU temperature using vcgencmd
        result = subprocess.check_output(["vcgencmd", "measure_temp"]).decode()
        # Extract temperature value from output
        match = re.search(r"temp=([\d\.]+)'C", result)
        if match:
            return {"cpu_temp_c": float(match.group(1))}
        else:
            raise HTTPException(status_code=500, detail="Could not parse CPU temp")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tts")
async def text_to_speech(text: str):
    # Ensure text parameter is provided
    if not text:
        raise HTTPException(status_code=400, detail="Text query parameter cannot be empty.")
    
    audio_path = None
    lock_file_path = get_lock_file_path()

    try:
        # Generate TTS audio file asynchronously
        audio_path = await fetch_tts_audio(text)

        if audio_path and os.path.exists(audio_path):
            try:
                # Create lock file before playing audio
                with open(lock_file_path, 'w') as f:
                    pass 
                # Play the audio file using aplay, suppressing output
                subprocess.run(
                    ['aplay', audio_path], 
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            finally:
                # Remove lock file after playback
                if os.path.exists(lock_file_path):
                    os.remove(lock_file_path)
            
            # Return the audio file as a response
            return FileResponse(audio_path, media_type="audio/wav", filename="output.wav")
        else:
            print(f"TTS audio file not generated or not found at {audio_path}")
            raise HTTPException(status_code=500, detail="Failed to generate or find TTS audio file.")
    except Exception as e:
        # Ensure lock file is removed in case of error
        if os.path.exists(lock_file_path):
            os.remove(lock_file_path)
        
        print(f"Error in TTS endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred during TTS processing: {str(e)}")

if __name__ == "__main__":
    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)