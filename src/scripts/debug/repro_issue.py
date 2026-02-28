import os
import sys
import traceback

file_path = "data/mediauploads/conversation1.mp4"

print(f"Testing MoviePy on: {file_path}")

try:
    print("Attempting import...")
    try:
        from moviepy import AudioFileClip
        print("Imported from moviepy")
    except ImportError:
        from moviepy.editor import AudioFileClip
        print("Imported from moviepy.editor")

    print("Attempting instantiation...")
    audio_clip = AudioFileClip(file_path)
    print("Instantiation success.")
    
    print("Attempting write...")
    audio_clip.write_audiofile("test_output.mp3", logger=None)
    print("Write success.")
    
    audio_clip.close()
    if os.path.exists("test_output.mp3"):
        os.remove("test_output.mp3")

except Exception:
    traceback.print_exc()
