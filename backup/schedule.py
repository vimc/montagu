#!/usr/bin/env python3
from os.path import abspath, dirname, join

from crontab import CronTab


def clear_existing():
    existing = cron.find_command(backup_script)
    for job in existing:
        cron.remove(job)


def schedule():
    job = cron.new(command=backup_script, comment="Duplicati backup")
    job.hour.on(2)
    job.day.every(1)
    job.run()


if __name__ == "__main__":
    here = dirname(abspath(__file__))
    backup_script = join(here, "backup.py")

    cron = CronTab()
    clear_existing()
    schedule()
    cron.write("montagu.tab")
