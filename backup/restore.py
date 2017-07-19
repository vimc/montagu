#!/usr/bin/env python3
import sys
from subprocess import run

from settings import load_settings, shared_args

if __name__ == "__main__":
    settings = load_settings()

    print("Doing pre-restore step")
    for target in settings.targets:
        print("- " + target.id)
        target.before_restore()

    print("Beginning restore")
    cmd = ["duplicati-cli", "restore", settings.remote_url]
    cmd += sys.argv[1:]
    cmd += shared_args(settings)
    run(cmd)

    print("Doing post-restore step")
    for target in settings.targets:
        print("- " + target.id)
        target.after_restore()
