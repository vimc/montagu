#!/usr/bin/env python3

import backup
import database
from notify import Notifier
from service import service
from settings import get_settings
from os.path import abspath, dirname
from os import chdir
from cli import add_test_user

def restore_db():
    settings = get_settings(False)
    notifier = Notifier(settings['notify_channel'])
    try:
        ok = service.status == 'running' and service.volume_present
        if not ok:
            raise Exception('montagu not in a state we can restore')
        backup.restore(settings)
        database.setup(settings)
        if settings["add_test_user"] is True:
            add_test_user()
        notifier.post("*Restored* data from backup on `{}` :recycle:".format(
            settings['instance_name']))
    except Exception as e:
        print(e)
        try:
            notifier.post("*Failed* to restore data on `{}` :bomb:",
                          settings['instance_name'])
        except:
            raise

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    restore_db()
