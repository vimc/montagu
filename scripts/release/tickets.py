import os
import re
import requests

from branch_diff import get_branch_diff

branch_pattern = re.compile(r"^i(\d+)($|[_-])")
NOT_FOUND = "NOT FOUND"


def get_token():
    token = os.environ.get('YOUTRACK_TOKEN')
    if not token:
        print("""Please set your YouTrack token as follows:
    export YOUTRACK_TOKEN=xxx
You may wish to add this line to your Bash ~/.profile

You can obtain a new token by following the instructions at
https://www.jetbrains.com/help/youtrack/standalone/Manage-Permanent-Token.html
""")
        exit(-1)
    return token


class Ticket:
    def __init__(self, data):
        self.id = data["id"]
        self.fields = {}
        for field in data["field"]:
            self.fields[field["name"]] = field["value"]

    def get(self, field):
        return self.fields[field]

    def state(self):
        return ", ".join(self.get("State"))

    def okay_to_release(self):
        return "Ready to deploy" in self.get("State")


class YouTrackHelper:
    base_url = "https://vimc.myjetbrains.com/youtrack/rest/"

    def __init__(self):
        self.token = get_token()

    def get_tickets(self, branch_names):
        for branch in branch_names:
            match = branch_pattern.match(branch)
            if match:
                yield self.get_ticket(branch, match.group(1))
            else:
                yield branch, None

    def get_ticket(self, branch, id):
        full_id = "VIMC-" + id
        r = self.get("issue/" + full_id)
        if r.status_code == 200:
            return branch, Ticket(r.json())
        else:
            return branch, NOT_FOUND

    def get(self, url_fragment):
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json"
        }
        url = self.base_url + url_fragment
        return requests.get(url, headers=headers)


def check_tickets(latest_tag):
    diff = get_branch_diff(latest_tag)
    print("Since then, the following branches have been merged in:")
    print(" ".join(diff))
    print("")

    yt = YouTrackHelper()
    pairs = list(yt.get_tickets(diff))
    problems = False
    for (branch, ticket) in pairs:
        if ticket is None:
            pass
        elif ticket == NOT_FOUND:
            print("Unable to find ticket corresponding to branch " + branch)
            problems = True
        elif not ticket.okay_to_release():
            template = "* {ticket} is in state {state}"
            print(template.format(ticket=ticket.id, state=ticket.state()))
            problems = True

    if problems:
        answer = input("Are you sure you want to proceed? (y/N) ")
        if answer != "y":
            exit(-1)

    return pairs