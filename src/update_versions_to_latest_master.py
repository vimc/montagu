#!/usr/bin/env python3
import os
import pprint
from os.path import join
from subprocess import run

import versions

if __name__ == "__main__":
    run(["git", "submodule", "update", "--recursive", "--remote"])
    print("\nNew versions:")
    pprint.pprint(versions.as_dict())
