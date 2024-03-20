#!/usr/bin/env bash
set -ex
./clear-docker.sh --force
function cleanup() {
    ./clear-docker.sh --force
    if [[ -d token_keypair ]]; then
        rm -rf token_keypair || sudo rm -rf token_keypair
    fi
}
trap cleanup EXIT

cp settings/buildkite.json src/montagu-deploy.json
pip3 install -r src/requirements.txt
./src/deploy.py
./src/test.py $@ --simulate-restart
