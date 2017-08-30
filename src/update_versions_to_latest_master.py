#!/usr/bin/env python3
from subprocess import run, PIPE


def parse(line):
    parts = line.split('\t')
    return parts[1], parts[0]


def get_version_for(repo_name, org="vimc"):
    url = "git@github.com:{org}/{name}".format(org=org, name=repo_name)
    text = run(["git", "ls-remote", url], check=True, stdout=PIPE, universal_newlines=True).stdout
    pairs = list(parse(line) for line in text.split('\n') if line)
    lookup = dict(pairs)
    commit = lookup["refs/heads/master"]
    return commit[:7]


if __name__ == "__main__":
    repo_map = [
        ("api", "montagu-api"),
        ("reporting_api", "montagu-reporting-api"),
        ("db", "montagu-db"),
        ("contrib_portal", "montagu-webapps"),
        ("admin_portal", "montagu-webapps"),
        ("report_portal", "montagu-webapps"),
        ("cert_tool", "montagu-cert-tool"),
        ("proxy", "montagu-proxy"),
        ("reports", "montagu-reports")
    ]

    with open('versions.py', 'w') as f:
        for key, repo in repo_map:
            version = get_version_for(repo)
            text = '{} = "{}"'.format(key, version)
            print(text)
            print(text, file=f)
