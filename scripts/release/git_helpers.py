from os.path import join
from subprocess import run, PIPE

import re


def get_submodule_version(path):
    full_path = join("submodules", path)
    result = run(["git", "-C", full_path, "rev-parse", "--short=7", "HEAD"],
                 stdout=PIPE, check=True, universal_newlines=True)
    return result.stdout.strip()


def get_past_submodule_version(path, master_repo_version):
    full_path = join("submodules", path)
    result = run(["git", "ls-tree", master_repo_version, full_path],
                 stdout=PIPE, check=True, universal_newlines=True).stdout

    # The output format is
    # <mode> SPACE <type> SPACE <object> TAB <file>
    # e.g. 160000 commit 6df8dcb6fb7b3d114552252782a4788f3349c6f9	src/models
    parts = re.split(r"\s+", result)
    if result:
        if len(parts) >= 4 and parts[1] == "commit":
            version = parts[2]
            return version[:7]
    else:
        print("Warning: Unable to find past version for submodule '{}'".format(
            path))
        return None

    template = "Unable to understand past Git status for submodule '{}': {}"
    raise Exception(template.format(path, result))
