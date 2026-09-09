#!/usr/bin/env bash
# Run this ONCE on the server, from the project root, right after
# `git pull` on this reorganized codebase, and BEFORE restarting the app.
#
# Why you need this: guestbook.json, feedback.json, notifications.json, etc.
# are in .gitignore, so git has never tracked them — `git pull` cannot move
# files it doesn't track. This script moves your real, live data files from
# the old root-level locations into the new data/ folder the code now
# expects. Templates, CSS/JS, and the python files were all tracked by git,
# so `git pull` already rearranged those for you automatically.
#
# Safe to re-run: it only moves a file if it still exists at the old path
# and won't overwrite anything already in data/.

set -e
mkdir -p data

FILES="guestbook.json playergameinfo.json uandp.json blog.json feedback.json \
spininfo.json notifications.json counter.json announcements.json links.json \
ranks.json"

for f in $FILES; do
    if [ -f "$f" ] && [ ! -f "data/$f" ]; then
        mv -v "$f" "data/$f"
    elif [ -f "$f" ]; then
        echo "skip $f -- data/$f already exists (not overwriting)"
    fi
done

echo "Done. site.db stays where it is; nothing else to move."
