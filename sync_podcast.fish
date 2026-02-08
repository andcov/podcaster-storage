#!/usr/bin/env fish

# 1. Re-generate all feeds
python3 gen_feed.py

# 2. Check if there are changes using porcelain output
# --porcelain is stable and designed for scripts
if test -n (git status --porcelain | string collect)
    echo "Syncing new files to GitHub..."
    
    # Add everything
    git add .
    
    # Create a commit with a timestamp
    set -l timestamp (date "+%Y-%m-%d %H:%M:%S")
    git commit -m "Update feeds: $timestamp"
    
    # Push to GitHub
    git push origin main
    
    echo "Done! Feeds updated."
else
    echo "No new files detected. Nothing to sync."
end
