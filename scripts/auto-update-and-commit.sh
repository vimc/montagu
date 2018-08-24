#!/usr/bin/env bash
set -ex
message=$(./src/update_versions_to_latest_master.py)
# https://stackoverflow.com/a/3879077/777939
git diff-index --quiet HEAD -- && echo "No changes detected" && exit 0
echo "Changes detected relative to origin/master"

# For some reason, the submodules must be added for "git diff --quiet"
# to behave as expected. But we were going to do that before commit anyway.
git add submodules
git diff --quiet origin/latest -- submodules && \
    echo "origin/latest contains submodule updates already" && exit 0
echo "Changes detected relative to origin/latest"
git reset

git remote set-url origin git@github.com:vimc/montagu
git push --delete origin latest || true
git branch -D latest || true
git checkout -b latest
git commit -m "Auto: Update versions to latest

$message"
git push -u origin latest
