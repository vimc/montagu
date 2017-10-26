#!/usr/bin/env python3
import sys

from helpers import run


class Branch:
    def __init__(self, remote, name):
        self.remote = remote
        self.name = name

    @classmethod
    def parse(cls, raw):
        if " -> " in raw:
            return None
        else:
            parts = raw.split('/')
            return Branch(parts[0], parts[1])


def get_branches_at(revision):
    raw = run("git branch -r --merged {}".format(revision))
    parsed = [Branch.parse(b) for b in raw.split('\n')]
    branches = set(b.name for b in parsed if b)
    return branches


def get_args():
    if len(sys.argv) != 2:
        print("""Usage: branch-diff REVISION

This will list all branches that are merged into the currently checked out
branch, but not into the named revision. This allows you to compare what you are
about to tag and deploy, to the previously tagged deploy. REVISION can be any
valid git identifier (hash, branch, tag)

e.g. branch-diff v0.4.0""")
        exit(-1)
    else:
        return sys.argv[1]


def get_branch_diff(here, compare_to):
    branches_here = get_branches_at(here)
    branches_there = get_branches_at(compare_to)
    return (branches_here - branches_there) - set(["master"])


if __name__ == "__main__":
    here = run("git rev-parse --short HEAD")
    compare_to = get_args()
    diff = get_branch_diff(here, compare_to)

    print("Branches merged into the current commit ({here}) but not into {compare_to}:".format(compare_to=compare_to, here=here))
    for branch in sorted(diff):
        print(branch)
