import os
import requests
from pathlib import Path

MEDIA_DIR = Path("data/mediauploads")
MEDIA_DIR.mkdir(parents=True, exist_ok=True)

SAMPLES = [
    {
        "name": "jfk_rice_moon_speech.ogg",
        "url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Kennedy_Rice_moon_speech_1.ogg", # Wikipedia with Chrome UA
        "desc": "Speech: JFK Rice University 'We choose to go to the moon' (~18 mins)"
    },
    {
        "name": "harvard_sentences.wav",
        "url": "https://github.com/realpython/python-speech-recognition/raw/master/audio_files/harvard.wav", # Confirmed working
        "desc": "Speech: Harvard Sentences (Clear Speech Test)"
    },
    {
        "name": "sintel_trailer.mp4",
        "url": "https://media.w3.org/2010/05/sintel/trailer.mp4", # W3C Sample with dialogue
        "desc": "Video: Sintel Trailer (MP4 with dialogue)"
    }
]

def download_file(url, filename, desc):
    path = MEDIA_DIR / filename
    print(f"Downloading {desc}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved to {path}")
        return str(path)
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        return None

if __name__ == "__main__":
    print(f"Downloading samples to {MEDIA_DIR.absolute()}")
    for sample in SAMPLES:
        # Convert .ogg to .mp3 naming if needed, but Whisper handles OGG. 
        # I'll keep original Extensions where possible or just save as is.
        # Actually JFK url ends in .ogg, so let's name it .ogg
        fname = sample["name"]
        if sample["url"].endswith(".ogg") and not fname.endswith(".ogg"):
            fname = fname.replace(".mp3", ".ogg")
            
        download_file(sample["url"], fname, sample["desc"])
    
    print("\nDone! You can now select these files in the 'Multimodal RAG Assistant' tab.")
