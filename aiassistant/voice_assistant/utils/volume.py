import subprocess
import datetime

def set_volume(percent):
    """
    Set the system volume on a Raspberry Pi to a specific percentage.
    Example: set_volume(50) sets volume to 50%.
    """
    try:
        subprocess.run(['amixer', 'set', 'Master', f'{percent}%'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to set volume: {e}")

def adjust_volume_by_time():
    """
    Adjust volume based on current time:
    - between 09:00 and 20:00 → 45%
    - otherwise → 30%
    """
    now = datetime.datetime.now().time()
    if datetime.time(9, 0) <= now < datetime.time(20, 0):
        pct = 60
    else:
        pct = 45
    set_volume(pct)