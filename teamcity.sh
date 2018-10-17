#!/usr/bin/env bash
set -ex
cp settings/teamcity.json src/montagu-deploy.json
pip3 install --quiet -r src/requirements.txt
./src/deploy.py
./src/test.py $@ --simulate-restart
