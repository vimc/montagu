#!/usr/bin/env python3

import database
import backup
from service import service
from settings import get_settings
from os.path import abspath, dirname
from os import chdir

def restore_db():
    ok = service.status == 'running' and service.volume_present
    if not ok:
        raise Exception('montagu not in a state we can restore')
    settings = get_settings(False)
    backup.restore(settings)
    database.setup(settings["use_real_passwords"])

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    restore_db()
