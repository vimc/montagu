#!/usr/bin/env python3
from os.path import abspath, dirname, join, isfile

import settings
from crontab import CronTab

tab_path = "/etc/cron.d/montagu"


def clear_existing():
    existing = cron.find_command(backup_script)
    for job in existing:
        cron.remove(job)


def schedule():
    job = cron.new(command=backup_script, comment="Duplicati backup", user="root")
    job.day.every(1)
    job.hour.on(2)
    job.minute.on(0)
    print("Running scheduled job now as a test. Output will be logged to " + settings.log_dir)
    job.run()

if __name__ == "__main__":
    here = dirname(abspath(__file__))
    print("Scheduling backup task")
    backup_script = join(here, "backup.py")
    if isfile(tab_path):
        cron = CronTab(tabfile=tab_path, user=False)
    else:
        cron = CronTab()
    clear_existing()
    schedule()
    cron.write(tab_path)

    print("Completed scheduling")
