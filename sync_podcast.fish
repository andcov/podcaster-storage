#!/usr/bin/env fish

# 1. Update the XML feeds
python3 gen_feed.py

# 2. Check for changes
if test -n "$(git status --porcelain)"
    echo "Syncing to GitHub..."
    git add .
    
    set -l timestamp (date "+%H:%M:%S")
    git commit -m "Podcast Sync: $timestamp"
    
    if git push origin main
        osascript -e "display notification \"Feeds pushed to GitHub\" with title \"🎙️ Podcast Sync\""
        echo "Push successful."
    else
        echo "Error: Git push failed."
    end
else
    echo "No changes detected."
end
