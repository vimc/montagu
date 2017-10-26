#!/usr/bin/env python3
import re

from helpers import run
from branch_diff import get_branch_diff

release_tag_pattern = re.compile(r"^v\d\.\d\.\d(-RC\d)?$")
dry_run = True


def get_latest_release_tag():
    tags = run("git tag").split('\n')
    release_tags = sorted(t for t in tags if release_tag_pattern.match(t))
    return release_tags[-1]


def git_is_clean():
    return not run("git status -s")


def tag(tag_name, branch_diff):
    message = "Release {tag}, incorporating these branches: {branches}".format(tag=tag_name, branches=branch_diff)
    run("git tag -a {tag} -m \"{msg}\"".format(tag=tag_name, msg=message))


def push():
    if not dry_run:
        run("git push --tags")


if __name__ == "__main__":
    if False:  # not git_is_clean():
        print("Git status reports as not clean; aborting release")
    else:
        latest_tag = get_latest_release_tag()
        print("The latest release was " + latest_tag)

        diff = get_branch_diff(latest_tag)
        print("Since then, the following branches have been merged in:")
        print(" ".join(diff))
        print("")

        new_tag = "v" + input("What should the new release tag be? v")
        print("Tagging and pushing...")
        tag(new_tag, diff)
        push()


