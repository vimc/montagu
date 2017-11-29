#!/usr/bin/env python3
from os import chdir
from os.path import abspath, dirname

# NOTE: if you remove 'import backup' here, then running this script
# will fail for mysterious reasons - it looks like a circular
# dependency but it seems weird that this would break it.
import backup
import service
from settings import get_settings

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    settings = get_settings(False)
    service.service.stop(settings)
