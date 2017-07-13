#!/usr/bin/env python3
import logging
from datetime import date
from os.path import join, isdir
from subprocess import Popen, CalledProcessError, PIPE, check_output

from settings import load_settings, get_secrets, shared_args

log_dir = '/var/log/duplicati'


def ensure_dir_exists(path):
    if not isdir(log_dir):
        check_output(["sudo", "mkdir", "-p", log_dir])
        #check_output(["sudo", "chmod", "666", log_dir])
        check_output(["setfacl", "-d", "-m", "666"])


def setup_logging():
    ensure_dir_exists(log_dir)
    filename = join(log_dir, "duplicati_{}.log".format(date.today().isoformat()))
    log_format = "%(asctime)s    %(message)s"
    logging.basicConfig(filename=filename, level=logging.DEBUG, format=log_format)


def run_duplicati(remote_url, paths):
    cmd = ["duplicati-cli", "backup", remote_url] + paths + shared_args(get_secrets())
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            print(line, end='')

    if p.returncode not in [0, 1]:
        raise CalledProcessError(p.returncode, p.args)


if __name__ == "__main__":
    setup_logging()
    settings = load_settings()
    print("Backing up the following files to {remote_url}: ".format(**settings))
    for path in settings["paths"]:
        print("- " + path)

    run_duplicati(settings["remote_url"], settings["paths"])
