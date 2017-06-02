import webbrowser

import data_import
from api_setup import configure_api
from service import get_service
from settings import get_settings


def backup():
    pass


def setup_new_data_volume():
    pass


def migrate_schema(db_password):
    pass


def generate_passwords():
    return {
        "api": None,
        "schema_migrator": None,
        "keystore_password": "password"
    }


def set_passwords_for_db_users(passwords):
    pass


def is_montagu_running(service):
    is_running = service.is_running
    if is_running:
        print("Montagu is running")
    else:
        print("Montagu not detected. Proceeding with first time setup")
    return is_running


def deploy():
    print("Beginning Montagu deploy")
    service = get_service()
    is_running = is_montagu_running(service)
    is_first_time = not is_running

    settings = get_settings(is_first_time)
    if is_running:
        service.stop()
        backup()

    if settings["persist_data"] and is_first_time:
        setup_new_data_volume()

    service.start()
    passwords = generate_passwords()
    set_passwords_for_db_users(passwords)

    migrate_schema(passwords['schema_migrator'])
    if is_first_time or not settings["persist_data"]:
        data_import.do(settings)

    configure_api("self-signed", passwords['api'], passwords["keystore_password"])

    print("Finished deploying Montagu")
    webbrowser.open("https://localhost:8080/")
    webbrowser.open("http://localhost:8081/")

if __name__ == "__main__":
    deploy()
