#!/usr/bin/env python3
import sys
from subprocess import run

from settings import load_settings, shared_args

if __name__ == "__main__":
    settings = load_settings()
    cmd = ["duplicati-cli", "restore", settings.remote_url]
    cmd += sys.argv[1:]
    cmd += shared_args(settings)
    run(cmd)
