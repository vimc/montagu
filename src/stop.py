#!/usr/bin/env python3
from os import chdir
from os.path import abspath, dirname

from service import MontaguService
from settings import get_settings

if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    settings = get_settings()
    MontaguService(settings).stop()
