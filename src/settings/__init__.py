import json
from os.path import abspath

from settings.boolean import BooleanSettingDefinition
from settings.definition import SettingDefinition
from settings.enum import EnumSettingDefinition

path = 'montagu-deploy.json'

definitions = [
    BooleanSettingDefinition("persist_data",
                             "Should data in the database be persisted?",
                             "If you answer no all data will be deleted from the database when Montagu is stopped. Data"
                             " should be persisted for live systems, and not persisted for testing systems.",
                             default_value=True),
    BooleanSettingDefinition("backup",
                             "Should data be backed up remotely?",
                             "This should be enabled for the production environment.",
                             default_value=True),
    EnumSettingDefinition("initial_data_source",
                          "What data should be imported initially?",
                          [
                              ("none", "Empty database"),
                              ("minimal", "Minimum required for Montagu to work (this includes enum tables and "
                                          "permissions)"),
                              ("test_data", "Fake data, useful for testing"),
                              ("legacy", "Imported data from SDF versions 6, 7, 8 and 12"),
                              # ("restore", "Restore from backup")
                          ]
                          ),
    SettingDefinition("backup_bucket",
                      "Which S3 bucket should be used for backup?",
                      "This is where data will be restored from, if you specified that a restore should happen for the"
                      "initial data import, and it's where data will be backed up to if you enabled backups.",
                      default_value="montagu-production"),
    BooleanSettingDefinition("open_browser",
                             "Open the browser after deployment?",
                             "If you answer yes, Montagu will be opened after deployment",
                             default_value=True),
    SettingDefinition("port",
                      "What port should Montagu listen on?",
                      "Note that this port must be the one that users browsers will be connecting to. In other words, "
                      "if there is another layer wrapping around Montagu (e.g. if it is being deployed to a VM) the "
                      "real port exposed on the physical machine must agree with the port you choose now.",
                      default_value=443),
    EnumSettingDefinition("certificate",
                          "What SSL certificate should Montagu use?",
                          [
                              ("self_signed", "Use the non-secure self-signed certificate in the repository"),
                              ("self_signed_fresh", "Generate a new, non-secure self-signed certificate every deploy"),
                              # ("trusted", "The real McCoy")
                          ]
                          )
]


def load_settings():
    settings = {}

    try:
        with open(path, 'r') as f:
            data = json.load(f) or {}
    except FileNotFoundError:
        data = {}

    for d in definitions:
        key = d.name
        if key in data:
            settings[key] = data[key]

    return settings


def get_settings(do_first_time_setup: bool):
    settings = load_settings()
    missing = list(d for d in definitions if d.name not in settings)
    if not do_first_time_setup:
        missing = list(d for d in missing if not d.first_time_only)

    if any(missing):
        print("I'm going to ask you some questions to determine how Montagu should be deployed.\n"
              "Your answers will be stored in {}.".format(abspath(path)))

        for d in missing:
            key = d.name
            value = d.ask()
            settings[key] = value

    save_settings(settings)
    print("Using these settings from {}:".format(abspath(path)))
    for k, v in settings.items():
        print("- {}: {}".format(k, v))

    return settings


def save_settings(settings):
    with open(path, 'w') as f:
        json.dump(settings, f, indent=4)
