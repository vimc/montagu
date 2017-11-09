from os.path import join
from subprocess import run, PIPE

import re


def get_submodule_version(path):
    full_path = join("submodules", path)
    result = run(["git", "submodule", "status", full_path], stdout=PIPE,
                 check=True, universal_newlines=True).stdout
    if result[0] in [" ", "+", "-"]:
        parts = result[1:].split(" ")
        commit_hash = parts[0]
        if re.match(r"[0-9a-f]{40}", commit_hash):
            version = commit_hash[:7]
            return version

    template = "Unable to understand Git status for submodule '{}': {}"
    raise Exception(template.format(path, result))


def get_past_submodule_version(path, master_repo_version):
    full_path = join("submodules", path)
    result = run(["git", "ls-tree", master_repo_version, full_path],
                 stdout=PIPE, check=True, universal_newlines=True).stdout

    # The output format is
    # <mode> SPACE <type> SPACE <object> TAB <file>
    # e.g. 160000 commit 6df8dcb6fb7b3d114552252782a4788f3349c6f9	src/models
    parts = re.split(r"\s+", result)
    if len(parts) >= 4 and parts[1] == "commit":
        version = parts[2]
        return version[:7]

    template = "Unable to understand past Git status for submodule '{}': {}"
    raise Exception(template.format(path, result))
