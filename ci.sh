#!/usr/bin/env bash
set -ex
./scripts/clear-docker.sh --force
function cleanup() {
    ./clear-docker.sh --force
}
trap cleanup EXIT

cp settings/teamcity.json src/montagu-deploy.json
pip3 install --quiet -r src/requirements.txt
./src/deploy.py
./src/test.py $@ --simulate-restart
./scripts/clear-docker.sh
