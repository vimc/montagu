#!/usr/bin/env bash
set -e
cp teamcity-settings.json src/montagu-deploy.json
pip3 install --quiet -r src/requirements.txt
./src/deploy.py
./src/test.py $@ --simulate-reboot
