#!/usr/bin/env python3
from os import chdir
from os.path import abspath, dirname

import backup
import service
from settings import get_settings

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    settings = get_settings(False)
    service.service.stop(settings)
