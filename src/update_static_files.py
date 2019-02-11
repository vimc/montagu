from os.path import abspath, dirname
from os import chdir
from settings import get_settings
from service import MontaguService
from service_config.static_server_config import configure_static_files
import paths


def update_static_files():
    settings = get_settings()
    service = MontaguService(settings)
    ok = service.status == 'running' and settings["copy_static_files"] is True
    if not ok:
        raise Exception('montagu not in a state we can update static files')
    try:
        configure_static_files(service)
    finally:
        paths.delete_safely(paths.static)


if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    update_static_files()
