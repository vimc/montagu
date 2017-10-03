import re
import datetime
import versions
import settings
import json
import os.path

path_last_restore = 'last_restore'
path_last_deploy = 'last_deploy.json'

def timestring():
    return str(datetime.datetime.now())

def dict_from_module(module):
    valid = re.compile('^[a-z][a-z_]*[a-z]$')
    return {key: getattr(module, key) for key in dir(module)
            if valid.match(key)}

def last_restore_read():
    last = None
    if os.path.exists(path_last_restore):
        with open(path_last_restore, 'r') as f:
            last = f.read().strip()
    return last

def last_restore_update():
    with open(path_last_restore, 'w') as f:
        f.write(timestring() + '\n')

def last_deploy_update(montagu_version):
    our_settings = settings.load_settings()
    last_restore = None
    if our_settings['initial_data_source'] == 'restore':
        last_restore = last_restore_read()
    dat = {
        'time': str(datetime.datetime.now()),
        'versions': dict_from_module(versions),
        'settings': our_settings,
        'last_restore': last_restore,
        'montagu': montagu_version}
    }
    with open(path_last_deploy, 'w') as f:
        json.dump(dat, f, indent = 4)
