#!/usr/bin/env bash
set -e
pip3 install -r src/requirements.txt
python3 ./src/deploy.py
