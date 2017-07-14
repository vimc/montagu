#!/usr/bin/env python3
from os.path import abspath, dirname, join, isfile

from crontab import CronTab

import settings

tab_path = "/etc/cron.d/montagu"


def clear_existing():
    existing = cron.find_command(backup_script)
    for job in existing:
        cron.remove(job)


def schedule():
    job = cron.new(command=backup_script, comment="Duplicati backup", user="root")
    job.hour.on(2)
    job.day.every(1)
    print("Running scheduled job now as a test. Output will be logged to " + settings.log_dir)
    job.run()

if __name__ == "__main__":
    here = dirname(abspath(__file__))
    if not isfile(settings.config_path) or not isfile(settings.list_path):
        print("Missing config files in {}. First copy files from configs/".format(settings.root_path))
        print("For example, for setting up backups on the support machine:")
        print("mkdir -p {0} && cp configs/support.montagu/* {0}".format(settings.root_path))
        exit(-1)

    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    s = settings.load_settings()
    settings.save_secrets(s.encrypted)

    print("Scheduling backup task")
    backup_script = join(here, "backup.py")
    if isfile(tab_path):
        cron = CronTab(tabfile=tab_path)
    else:
        cron = CronTab()
    clear_existing()
    schedule()
    cron.write(tab_path)

    print("Completed setup")
