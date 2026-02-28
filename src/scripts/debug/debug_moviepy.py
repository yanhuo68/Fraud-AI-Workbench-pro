import sys
try:
    import moviepy
    print(f"MoviePy Path: {moviepy.__file__}")
    print(f"MoviePy Version: {moviepy.__version__}")
except Exception as e:
    print(f"Error importing moviepy: {e}")

print("\n--- Attempting: from moviepy import VideoFileClip ---")
try:
    from moviepy import VideoFileClip
    print("SUCCESS: from moviepy import VideoFileClip")
except ImportError as e:
    print(f"FAILURE: {e}")

print("\n--- Attempting: from moviepy.editor import VideoFileClip ---")
try:
    from moviepy.editor import VideoFileClip
    print("SUCCESS: from moviepy.editor import VideoFileClip")
except ImportError as e:
    print(f"FAILURE: {e}")

print("\n--- Attempting: from moviepy.video.io.VideoFileClip import VideoFileClip ---")
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    print("SUCCESS: from moviepy.video.io.VideoFileClip import VideoFileClip")
except ImportError as e:
    print(f"FAILURE: {e}")
