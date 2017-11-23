#!/usr/bin/env python3
"""
Tags a release and writes out a changelog, first checking that associated
tickets are in the correct status. The changelog is written to RELEASE_LOG.md
and includes ticket summaries from YouTrack, where applicable

Usage:
  make-release.py [--test-run]

Options:
  --test-run    Don't insist on Git being in a clean state
"""

import re

from io import StringIO

from docopt import docopt

from helpers import run
from tickets import check_tickets, tag_tickets

release_tag_pattern = re.compile(r"^v\d\.\d\.\d(-RC\d)?$")


def get_latest_release_tag():
    tags = run("git tag").split('\n')
    release_tags = sorted(t for t in tags if release_tag_pattern.match(t))
    return release_tags[-1]


def git_is_clean():
    return not run("git status -s")


def tag(tag_name, branch_diff):
    message = "Release {tag}, incorporating these branches: {branches}".format(
        tag=tag_name, branches=branch_diff)
    run("git tag -a {tag} -m \"{msg}\"".format(tag=tag_name, msg=message))


def get_new_tag():
    new_tag = "v" + input("What should the new release tag be? v")
    if new_tag <= latest_tag:
        template = "Error: {new_tag} is not after {latest_tag}"
        print(template.format(new_tag=new_tag, latest_tag=latest_tag))
        exit(-1)
    if not release_tag_pattern.match(new_tag):
        print("Error: tag does not correspond to regex")
        exit(-1)
    return new_tag


def make_release_message(tag, branches_and_tickets):
    with StringIO() as msg:
        print("# " + tag, file=msg)
        print("", file=msg)
        print("## Tickets", file=msg)
        for branch, ticket in branches_and_tickets:
            if ticket:
                summary = ticket.get("summary")
                line = "* {branch}: {summary}".format(branch=branch,
                                                      summary=summary)
                print(line, file=msg)

        print("\n## Other branches merged in this release", file=msg)
        for branch, ticket in branches_and_tickets:
            if not ticket:
                print("* " + branch, file=msg)
        return msg.getvalue()


def write_release_log(message):
    with open('RELEASE_LOG.md', 'a') as f:
        f.write(message)
        f.write("\n")


def commit_and_tag():
    run("git add RELEASE_LOG.md")
    run("git commit -m \"{msg}\"".format(msg=release_message))
    print("Tagging...")
    tag(new_tag, release_message)


def fetch():
    print("Fetching from remote...")
    run("git fetch --tags --all")


if __name__ == "__main__":
    args = docopt(__doc__)

    if not (git_is_clean() or args["--test-run"]):
        print("Git status reports as not clean; aborting making release")
    else:
        fetch()
        latest_tag = get_latest_release_tag()
        print("The latest release was " + latest_tag)

        branches_and_tickets = check_tickets(latest_tag)
        new_tag = get_new_tag()

        print("Writing release log...")
        release_message = make_release_message(new_tag, branches_and_tickets)
        write_release_log(release_message)
        commit_and_tag()
        ticket_ids = list(ticket.id for branch, ticket in branches_and_tickets)
        tag_tickets(branches_and_tickets, new_tag)

        print("""Done"
No changes have been pushed, so please review and then push using 

git push --follow-tags

When you come to deploy this release, the RELEASE_LOG.md file
(or the commit message) will tell you which tickets need to be updated""")
