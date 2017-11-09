#!/usr/bin/env python3
import os
import pprint
from os.path import join
from subprocess import run

import versions

if __name__ == "__main__":
    root = "submodules"
    for submodule in os.listdir(root):
        full_path = join(root, submodule)
        print(submodule + ": ", end="", flush=True)
        run(["git", "checkout", "master", "--quiet"], cwd=full_path, check=True)
        run(["git", "pull"], cwd=full_path, check=True)

    print("\nNew versions:")
    pprint.pprint(versions.as_dict())
