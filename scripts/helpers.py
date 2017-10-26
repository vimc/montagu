import subprocess

def run(cmd):
    parts = cmd.split(" ")
    result = subprocess.run(parts, check=True, stdout=subprocess.PIPE, universal_newlines=True)
    return result.stdout.strip()
