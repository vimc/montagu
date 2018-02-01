#!/usr/bin/env python3
import pprint
from subprocess import run

import versions

if __name__ == "__main__":
    run(["git", "submodule", "update", "--remote"])
    print("\nNew versions:")
    pprint.pprint(versions.as_dict())
