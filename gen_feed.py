import os
import subprocess
from datetime import datetime
from feedgen.feed import FeedGenerator
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

BASE_URL = "https://andcov.github.io/podcaster-storage"
AUDIO_ROOT = "audio"

def get_duration(file_path):
    """Uses ffprobe to get duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return str(int(float(result.stdout.strip())))
    except:
        return "0"

def get_title(file_path, filename):
    """Tries to get ID3 title, falls back to filename."""
    try:
        audio = EasyID3(file_path)
        return audio['title'][0]
    except:
        return filename.replace(".mp3", "").replace("_", " ")

def create_feed(folder_name, files):
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    title = folder_name.replace("-", " ").title()
    fg.title(title)
    fg.description(f"Sync for {title}")
    fg.link(href=f"{BASE_URL}/{folder_name}.xml", rel='self')
    
    # Check for cover art in the folder
    cover_path = os.path.join(AUDIO_ROOT, folder_name, "cover.jpg")
    if os.path.exists(cover_path):
        fg.logo(f"{BASE_URL}/{AUDIO_ROOT}/{folder_name}/cover.jpg")

    for filename in sorted(files):
        file_path = os.path.join(AUDIO_ROOT, folder_name, filename)
        fe = fg.add_entry()
        
        # Metadata Extraction
        fe.title(get_title(file_path, filename))
        fe.podcast.itunes_duration(get_duration(file_path))
        
        # Use file modification time as pubDate
        file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
        fe.published(file_mtime.strftime('%a, %d %b %Y %H:%M:%S +0000'))
        
        file_url = f"{BASE_URL}/{AUDIO_ROOT}/{folder_name}/{filename}".replace(" ", "%20")
        fe.enclosure(file_url, 0, 'audio/mpeg')
    
    fg.rss_file(f"{folder_name}.xml", pretty=True)
    print(f"✅ Generated: {folder_name}.xml")

def main():
    for entry in os.scandir(AUDIO_ROOT):
        if entry.is_dir():
            audio_files = [f for f in os.listdir(entry.path) if f.endswith('.mp3')]
            if audio_files:
                create_feed(entry.name, audio_files)

if __name__ == "__main__":
    main()
