#!/usr/bin/env bash
set -e
git fetch --all
latest=$(git tag -l 'v*' | sort | tail -n 1)
echo -n "Which tag do you want to deploy? [$latest] "
read version
version=${version:-$latest}

echo "Checking out $version"
git checkout $version
git submodule update

pip3 install --quiet -r src/requirements.txt
python3 ./src/deploy.py
