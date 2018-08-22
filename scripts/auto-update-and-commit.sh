#!/usr/bin/env bash
set -ex
./src/update_versions_to_latest_master.py
git status --porcelain && echo "No changes detected" && exit 0;
echo "Changes detected"

git push --delete origin latest
git branch -d latest
git checkout -b latest

git commit -m "Auto: Update versions to latest"
git push -u origin
