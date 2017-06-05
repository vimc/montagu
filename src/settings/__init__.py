import json

from settings.boolean import BooleanSettingDefinition
from settings.enum import EnumSettingDefinition
from settings.definition import SettingDefinition

path = 'montagu-deploy.json'

definitions = [
    BooleanSettingDefinition("persist_data",
                             "Should data in the database be persisted?",
                             "If you answer no all data will be deleted from the database when Montagu is stopped. Data"
                             " should be persisted for live systems, and not persisted for testing systems.",
                             default_value=True),
    EnumSettingDefinition("initial_data_source",
                          "What data should be imported initially?",
                          [
                              ("none", "Empty database"),
                              # ("minimal",
                              #  "Minimum required for Montagu to work (this includes enum tables and permissions)"),
                              ("test_data", "Fake data, useful for testing"),
                              ("legacy", "Imported data from SDF versions 6, 7, 8 and 12"),
                              # ("restore", "Restore from backup")
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
              "Your answers will be stored in {}.".format(path))

        for d in missing:
            key = d.name
            value = d.ask()
            settings[key] = value

    save_settings(settings)
    return settings


def save_settings(settings):
    with open(path, 'w') as f:
        json.dump(settings, f, indent=4)
