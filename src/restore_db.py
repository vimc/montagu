#!/usr/bin/env python3

import database
import backup
from notify import Notifier
from service import service
from settings import get_settings
from os.path import abspath, dirname
from os import chdir
from cli import add_test_user

def restore_db():
    notifier = Notifier(settings['notify_channel'])
    try:
        ok = service.status == 'running' and service.volume_present
        if not ok:
            raise Exception('montagu not in a state we can restore')
        settings = get_settings(False)
        backup.restore(settings)
        database.setup(settings["password_group"])
        if settings["add_test_user"] is True:
            add_test_user()
        notifier.post("*Restored* data from backup on `{}` :recycle:".format(
            settings['instance_name']))
    except:
        try:
            notifier.post("*Failed* to restore data on `{}` :bomb:",
                          settings['instance_name'])
        except:
            pass

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    restore_db()
