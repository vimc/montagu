from subprocess import run

import pystache as pystache

import service

finished_setup = False


def configure(settings):
    with open("../backup/configs/production/config.json", 'r') as f:
        template = f.read()
    config = pystache.render(template, {
        "s3_bucket": settings["backup_bucket"],
        "db_container": service.db_name
    })
    with open("/etc/montagu/backup/config.json", 'w') as f:
        f.write(config)


def setup(settings):
    global finished_setup
    if not finished_setup:
        print("- Configuring and installing backup service")
        configure(settings)
        run("../backup/setup.sh", check=True)
        finished_setup = True


def backup(settings):
    print("Performing backup")
    setup(settings)
    run("../backup/backup.py", check=True)


def schedule(settings):
    print("Scheduling backup")
    setup(settings)
    run(["../backup/schedule.py", "--no-immediate-backup"], check=True)


def restore(settings):
    print("Restoring from remote backup")
    setup(settings)
    run(["../backup/restore.py"], check=True)
