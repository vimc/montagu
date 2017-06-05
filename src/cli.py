#!/usr/bin/env python3
import sys

from subprocess import run

import versions
from images import get_image_name

command = [
    "docker", "run",
    "-it",
    "--network", "montagu_default"
]
name = get_image_name("montagu-cli", versions.api)
args = sys.argv[1:]

run(command + [name] + args)
