#!/usr/bin/env bash
set -ex
./src/update_versions_to_latest_master.py
# https://stackoverflow.com/a/3879077/777939
git diff-index --quiet HEAD -- && echo "No changes detected" && exit 0;
echo "Changes detected"

git remote set-url origin git@github.com:vimc/montagu
git push --delete origin latest || true
git branch -D latest || true
git checkout -b latest

git add submodules
git commit -m "Auto: Update versions to latest"
git push -u origin latest
