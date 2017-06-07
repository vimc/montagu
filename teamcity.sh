#!/usr/bin/env bash
set -e
cp teamcity-settings.json src/montagu-deploy.json
cd src && ./deploy.py