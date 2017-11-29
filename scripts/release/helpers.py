import re
import subprocess
import shlex


def run(cmd, working_dir=None):
    parts = shlex.split(cmd)
    result = subprocess.run(parts, check=True, stdout=subprocess.PIPE,
                            universal_newlines=True, cwd=working_dir)
    return result.stdout.strip()

release_tag_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)(?:-RC(\d+))?$")

def get_latest_release_tag():
    tags = run("git tag").split('\n')
    release_tags = sorted(t for t in tags if release_tag_pattern.match(t))
    return release_tags[-1]

def validate_release_tag(tag):
    m = release_tag_pattern.match(tag)
    if not m:
        raise Exception("Tag {} does not correspond to pattern".format(tag))
    return m

def parse_version(tag):
    v = validate_release_tag(tag).groups()
    return [int(el) for el in v[:3]] + [float(v[3]) if v[3] else float("inf")]

def version_greater_than(target, than):
    return parse_version(target) > parse_version(than)
