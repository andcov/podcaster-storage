import os
from feedgen.feed import FeedGenerator

# --- CONFIGURATION ---
BASE_URL = "https://yourusername.github.io/your-repo-name"
AUDIO_ROOT = "audio"

def create_feed(folder_name, files):
    fg = FeedGenerator()
    fg.load_extension('podcast')
    
    # Use folder name as Podcast Title
    title = folder_name.replace("-", " ").replace("_", " ").title()
    fg.title(title)
    fg.description(f"Private feed for {title}")
    fg.link(href=f"{BASE_URL}/{folder_name}.xml", rel='self')
    
    # Sort files by date (newest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(AUDIO_ROOT, folder_name, x)), reverse=True)

    for filename in files:
        if filename.endswith(('.mp3', '.m4a')):
            fe = fg.add_entry()
            fe.title(filename)
            # URL structure: BASE_URL / audio / folder / file
            file_url = f"{BASE_URL}/{AUDIO_ROOT}/{folder_name}/{filename}".replace(" ", "%20")
            fe.enclosure(file_url, 0, 'audio/mpeg')
    
    output_path = f"{folder_name}.xml"
    fg.rss_file(output_path, pretty=True)
    print(f"✅ Generated: {output_path}")

def main():
    if not os.path.exists(AUDIO_ROOT):
        print("Create an /audio folder first!")
        return

    # Loop through every subfolder in /audio
    for entry in os.scandir(AUDIO_ROOT):
        if entry.is_dir():
            folder_name = entry.name
            audio_files = [f for f in os.listdir(entry.path) if f.endswith(('.mp3', '.m4a'))]
            
            if audio_files:
                create_feed(folder_name, audio_files)
            else:
                print(f"⚠️  Skipping '{folder_name}' (no audio files found)")

if __name__ == "__main__":
    main()
