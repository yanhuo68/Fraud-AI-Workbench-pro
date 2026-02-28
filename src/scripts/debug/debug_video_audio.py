import os
from moviepy import VideoFileClip

file_path = "data/mediauploads/conversation1.mp4"

print(f"Testing video file: {file_path}")

try:
    video = VideoFileClip(file_path)
    print(f"Video created. Duration: {video.duration}")
    print(f"Has audio attribute? {hasattr(video, 'audio')}")
    print(f"video.audio object: {video.audio}")
    
    if video.audio:
        print("Audio found. Attempting write...")
        video.audio.write_audiofile("debug_output.mp3", logger=None)
        print("Write success.")
    else:
        print("ERROR: video.audio is None.")
        
    video.close()

except Exception as e:
    print(f"Exception: {e}")
