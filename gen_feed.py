import os
import re
import subprocess
from datetime import datetime, timedelta
from feedgen.feed import FeedGenerator
from mutagen.easyid3 import EasyID3

# --- CONFIG ---
BASE_URL = "https://andcov.github.io/podcaster-storage"
AUDIO_ROOT = "audio"
START_DATE = datetime(2020, 1, 1, 12, 0, 0)

def get_duration(file_path):
    """Uses ffprobe to get duration in seconds."""
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file_path]
    try:
        return str(int(float(subprocess.check_output(cmd).decode().strip())))
    except: return "0"

def extract_number(filename):
    """Extracts the first number found in a filename."""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 999

def get_id3_title(file_path, filename):
    try:
        audio = EasyID3(file_path)
        return audio['title'][0]
    except:
        return filename.replace(".mp3", "").replace("_", " ")

def create_feed(folder_name, files):
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    # Metadata
    clean_title = folder_name.replace("-", " ").title()
    fg.title(clean_title)
    fg.description(f"Sync for {clean_title}")
    fg.link(href=f"{BASE_URL}/{folder_name}.xml", rel='self')

    # --- COVER ART ---
    if "cover.jpg" in os.listdir(os.path.join(AUDIO_ROOT, folder_name)):
        img_url = f"{BASE_URL}/{AUDIO_ROOT}/{folder_name}/cover.jpg"
        fg.image(img_url)
        fg.podcast.itunes_image(img_url)

    # --- CHOOSE SORTING LOGIC ---
    # We use "Serial" for Language Transfer or anything with 'Course' in the name
    is_serial = "Spanish" in folder_name or "Course" in folder_name
    
    if is_serial:
        fg.podcast.itunes_type('serial')
        # Sort by the number in the filename
        files.sort(key=extract_number)
    else:
        fg.podcast.itunes_type('episodic')
        # Sort by file modification date (default)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(AUDIO_ROOT, folder_name, x)), reverse=True)

    for index, filename in enumerate(files):
        if not filename.endswith('.mp3'): continue
        
        file_path = os.path.join(AUDIO_ROOT, folder_name, filename)
        fe = fg.add_entry()
        fe.title(get_id3_title(file_path, filename))
        
        # --- DATE LOGIC ---
        if is_serial:
            # Lesson 1 gets Day 1, Lesson 2 gets Day 2...
            lesson_num = extract_number(filename)
            pub_date = START_DATE + timedelta(days=lesson_num)
        else:
            # Use actual file modification time
            pub_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            
        fe.published(pub_date.strftime('%a, %d %b %Y %H:%M:%S +0000'))
        
        # Enclosure & Duration
        fe.podcast.itunes_duration(get_duration(file_path))
        file_url = f"{BASE_URL}/{AUDIO_ROOT}/{folder_name}/{filename}".replace(" ", "%20")
        fe.enclosure(file_url, 0, 'audio/mpeg')
    
    fg.rss_file(f"{folder_name}.xml", pretty=True)
    print(f"✅ Generated: {folder_name}.xml ({'Serial' if is_serial else 'Episodic'})")

def main():
    for entry in os.scandir(AUDIO_ROOT):
        if entry.is_dir():
            audio_files = [f for f in os.listdir(entry.path) if f.endswith('.mp3')]
            if audio_files:
                create_feed(entry.name, audio_files)

if __name__ == "__main__":
    main()
