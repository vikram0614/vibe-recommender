import yt_dlp
import os

AUDIO_DIR = "audio_clips"
os.makedirs(AUDIO_DIR, exist_ok=True)

def download_clip(artist, track, out_id):
    query = f"{artist} {track} audio"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{AUDIO_DIR}/{out_id}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
        'default_search': 'ytsearch1',
        'quiet': True,
        'postprocessor_args': ['-t', '30'],  # keep only first 30 seconds
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])
        return f"{AUDIO_DIR}/{out_id}.wav"
    except Exception as e:
        print(f"Failed: {artist} - {track}: {e}")
        return None