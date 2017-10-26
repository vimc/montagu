import subprocess
import shlex


def run(cmd):
    parts = shlex.split(cmd)
    result = subprocess.run(parts, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    return result.stdout.strip()
