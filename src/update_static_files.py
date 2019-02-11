from os.path import abspath, dirname
from os import chdir
from settings import get_settings
from service import MontaguService
from service_config.static_server_config import configure_static_files


def update_static_files():
    settings = get_settings()
    service = MontaguService(settings)
    ok = service.status == 'running' and settings["copy_static_files"] is True
    if not ok:
        raise Exception('montagu not in a state we can update static files')
    configure_static_files(service)


if __name__ == "__main__":
    abspath = abspath(__file__)
    chdir(dirname(abspath))
    update_static_files()
