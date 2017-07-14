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
        logging.error("An error occurred:", exc_info=e)


def run_duplicati(settings):
    cmd = ["duplicati-cli", "backup", settings.remote_url]
    cmd += settings.paths
    cmd += shared_args(settings)
    with Popen(cmd, stdout=PIPE, stderr=PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout.readlines():
            logging.info(line.strip())
        for line in p.stderr.readlines():
            logging.error(line.strip())

    if p.returncode not in [0, 1]:
        raise Exception("Duplicati backup process returned error code {}".format(p.returncode))


def run():
    settings = load_settings()
    logging.info("Backing up the following files to {}: ".format(settings.remote_url))
    for path in settings.paths:
        logging.info("- " + path)

    run_duplicati(settings)

if __name__ == "__main__":
    print("Running backup. Output will be logged to " + log_dir)
    with_logging(run)
