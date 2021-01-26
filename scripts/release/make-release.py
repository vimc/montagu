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

from io import StringIO

from docopt import docopt

from helpers import run, fetch
from release_tag import get_latest_release_tag, version_greater_than
from tickets import check_tickets, tag_tickets
from tickets import NOT_FOUND


def git_is_clean():
    return not run("git status -s")


def tag(tag_name, branch_diff):
    message = "Release {tag}, incorporating these branches: {branches}".format(
        tag=tag_name, branches=branch_diff)
    run("git tag -a {tag} -m \"{msg}\"".format(tag=tag_name, msg=message))


def get_new_tag(latest_tag):
    new_tag = "v" + input("What should the new release tag be? v")
    if not version_greater_than(new_tag, latest_tag):
        template = "Error: {new_tag} is not after {latest_tag}"
        print(template.format(new_tag=new_tag, latest_tag=latest_tag))
        exit(-1)
    return new_tag


def make_release_message(tag, branches_and_tickets):
    with StringIO() as msg:
        print("# " + tag, file=msg)
        print("", file=msg)
        print("## Tickets", file=msg)
        for branch, ticket in branches_and_tickets:
            if ticket == NOT_FOUND:
                pass
            else:
                summary = ticket.get("summary")
                line = "* {branch}: {summary}".format(branch=branch,
                                                      summary=summary)
                print(line, file=msg)
        print("\n## Other branches merged in this release", file=msg)
        for branch, ticket in branches_and_tickets:
            if ticket == NOT_FOUND:
                print("* " + branch, file=msg)
        return msg.getvalue()


def write_release_log(message):
    with open('RELEASE_LOG.md', 'a') as f:
        f.write(message)
        f.write("\n")


def commit_and_tag():
    run("git add RELEASE_LOG.md")
    run("git commit -m \"{msg}\"".format(msg=release_message))
    print("* Tagging")
    tag(new_tag, release_message)


def update_youtrack(branches_and_tickets, test_run):
    if test_run:
        print("* --test-run is enabled: Skipping updating YouTrack")
        return

    print("* Updating YouTrack")
    tickets = list(ticket for branch, ticket in branches_and_tickets)
    problems = tag_tickets(tickets, new_tag)
    if problems:
        print("Error updating YouTrack:")
        for problem in problems:
            print(problem)
        print("")


if __name__ == "__main__":
    args = docopt(__doc__)
    test_run = args["--test-run"]

    if not (git_is_clean() or test_run):
        print("Git status reports as not clean; aborting making release")
    else:
        fetch()
        latest_tag = get_latest_release_tag()
        print("The latest release was " + latest_tag)

        branches_and_tickets = check_tickets(latest_tag)
        new_tag = get_new_tag(latest_tag)

        print("* Writing release log")
        release_message = make_release_message(new_tag, branches_and_tickets)
        write_release_log(release_message)
        commit_and_tag()
        update_youtrack(branches_and_tickets, test_run)

        print("""---------------------------------------------------------------
Completed successfully. No changes have been pushed, so please review and then 
push using: 

  git push --follow-tags
  ./scripts/release/tag-images.py latest

Tickets have been tagged in YouTrack, so post release do the following:
* Go to 
  https://mrc-ide.myjetbrains.com/youtrack/issues?q=Fixed%20in%20build:%20{tag}
* Select all tickets and type "State: Deployed".""".format(tag=new_tag))
