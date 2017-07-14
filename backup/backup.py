#!/usr/bin/env python3
import logging
from datetime import date
from os import makedirs
from os.path import join, isdir
from subprocess import Popen, CalledProcessError, PIPE

from settings import load_settings, shared_args, log_dir


def ensure_dir_exists(dir_path):
    if not isdir(dir_path):
        makedirs(dir_path)


def with_logging(do):
    ensure_dir_exists(log_dir)
    filename = join(log_dir, "duplicati_{}.log".format(date.today().isoformat()))
    log_format = "%(asctime)s    %(message)s"
    logging.basicConfig(filename=filename, level=logging.DEBUG, format=log_format)
    logging.info("*" * 60)
    try:
        do()
    except Exception as e:
        logging.error(e)


def read_lines_from_reader(reader):
    line = ""
    for char in reader:
        if char != '\n':
            line += char
        else:
            yield line.strip()
            line = ""
    yield line.strip()


def run_duplicati(remote_url, paths, secrets):
    cmd = ["duplicati-cli", "backup", remote_url] + paths + shared_args(secrets)
    with Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in read_lines_from_reader(p.stdout):
            logging.info(line)
        for line in read_lines_from_reader(p.stderr):
            logging.error(line)

    if p.returncode not in [0, 1]:
        raise CalledProcessError(p.returncode, p.args)


def run():
    settings = load_settings()
    logging.info("Backing up the following files to {remote_url}: ".format(**settings))
    for path in settings["paths"]:
        logging.info("- " + path)

    run_duplicati(settings["remote_url"], settings["paths"], settings["secrets"])

if __name__ == "__main__":
    print("Running backup. Output will be logged to " + log_dir)
    with_logging(run)
