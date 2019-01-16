#!/usr/bin/env python3
from subprocess import run, DEVNULL

import versions

if __name__ == "__main__":
    previous = versions.as_dict()
    run(["git", "submodule", "update", "--remote"], stdout=DEVNULL)
    new = versions.as_dict()

    changed = dict()
    for submodule in previous.keys():
        if new[submodule] != previous[submodule]:
            changed[submodule] = (previous[submodule], new[submodule])

    if changed:
        print("The following submodules were updated:")
        width = max(len(s) for s in changed.keys())
        for submodule, versions in changed.items():
            old, new = versions
            print("{}: {} -> {}".format(submodule.ljust(width), old, new))
    else:
        print("No submodules needed to update")
