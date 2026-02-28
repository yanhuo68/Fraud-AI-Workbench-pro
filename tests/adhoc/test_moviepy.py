try:
    from moviepy.editor import AudioFileClip
    print("Success: from moviepy.editor import AudioFileClip")
except ImportError as e:
    print(f"Failed: moviepy.editor - {e}")

try:
    from moviepy import AudioFileClip
    print("Success: from moviepy import AudioFileClip")
except ImportError as e:
    print(f"Failed: from moviepy import AudioFileClip - {e}")
except Exception as e:
    print(f"Error: {e}")
