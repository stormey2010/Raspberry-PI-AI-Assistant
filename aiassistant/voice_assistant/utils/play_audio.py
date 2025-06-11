import subprocess

def play_audio(path):
    """Play a WAV file without blocking the main thread."""
    try:
        subprocess.Popen(
            ['aplay', path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"Failed to play sound {path}: {e}")