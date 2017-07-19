#!/usr/bin/env python3
from os.path import isfile

import settings

if __name__ == "__main__":
    if not isfile(settings.config_path):
        print("Missing config files in {}. First copy files from configs/".format(settings.root_path))
        print("For example, for setting up backups on the support machine:")
        print("mkdir -p {0} && cp configs/support.montagu/* {0}".format(settings.root_path))
        exit(-1)

    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    s = settings.load_settings()
    settings.save_secrets(s.encrypted)
