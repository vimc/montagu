#!/usr/bin/env python3
import sys

import os
from os.path import join

from git_helpers import get_submodule_version, get_past_submodule_version
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


class Difference:
    def __init__(self, past_version):
        self.diff = {}
        self.add_main_diff(past_version)
        for submodule in os.listdir("submodules"):
            self.add_submodule_diff(submodule, past_version)

    def add(self, branches, submodule):
        for b in branches:
            if b not in self.diff:
                self.diff[b] = []
            self.diff[b].append(submodule)

    def add_main_diff(self, past_version):
        self.add(Difference.get_branch_diff(past=past_version), "main")

    def add_submodule_diff(self, submodule, past_main_repo_version):
        full_path = join("submodules", submodule)
        current_version = get_submodule_version(submodule)
        previous_version = get_past_submodule_version(submodule,
                                                      past_main_repo_version)
        d = Difference.get_branch_diff(current_version, previous_version,
                                       working_dir=full_path)
        self.add(d, submodule)

    @classmethod
    def get_branches_at(cls, revision, working_dir=None):
        raw = run("git branch -r --merged {}".format(revision),
                  working_dir=working_dir)
        parsed = [Branch.parse(b) for b in raw.split('\n')]
        branches = set(b.name for b in parsed if b)
        return branches

    @classmethod
    def get_branch_diff(cls, current=None, past=None, working_dir=None):
        current = current or run("git rev-parse --short HEAD")
        branches_now = cls.get_branches_at(current, working_dir=working_dir)
        branches_then = cls.get_branches_at(past, working_dir=working_dir)
        return (branches_now - branches_then) - set(["master"])


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


<<<<<<< HEAD
=======
def get_branch_diff(compare_to):
    here = run("git rev-parse --short=7 HEAD")
    branches_here = get_branches_at(here)
    branches_there = get_branches_at(compare_to)
    return (branches_here - branches_there) - set(["master"])


>>>>>>> master
if __name__ == "__main__":
    compare_to = get_args()
    diff = Difference(compare_to)

    template = "Branches merged into the current commit " \
               "but not into {compare_to}:"
    print(template.format(compare_to=compare_to))
    for branch in sorted(diff.diff.keys()):
        repos = diff.diff[branch]
        print("{} ({})".format(branch, ", ".join(repos)))
