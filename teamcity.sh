#!/usr/bin/env bash
set -e
cp teamcity-settings.json src/montagu-deploy.json
cd src
pip3 install -r requirements.txt
./deploy.py