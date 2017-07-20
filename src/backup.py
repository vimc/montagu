from subprocess import run, check_output

import pystache as pystache

import service


def configure(settings):
    with open("../backup/configs/production/config.json", 'r') as f:
        template = f.read()
    config = pystache.render(template, {
        "s3_bucket": settings["backup_bucket"],
        "db_container": service.db_name
    })
    with open("/etc/montagu/backup/config.json", 'w') as f:
        f.write(config)


def backup(settings):
    print("Performing backup")
    configure(settings)
    run("../backup/setup.sh", check=True)
    run("../backup/backup.py", check=True)


def schedule(settings):
    print("Scheduling backup")
    configure(settings)
    run(["../backup/schedule.py", "--no-immediate-backup"], check=True)
