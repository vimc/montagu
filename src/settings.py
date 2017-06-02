import json

path = 'montagu-deploy.json'


class SettingDefinition:
    def __init__(self, name: str, question: str, guidance: str, default_value=None, first_time_only=False):
        self.name = name
        self.question = question
        self.guidance = guidance
        self.default_value = default_value
        self.first_time_only = first_time_only

    def ask(self):
        print("")
        print(self.question)
        print(self.guidance)
        answer = None
        prompt = self.get_prompt() + " "

        while answer is None:
            answer = self.parse(input(prompt))
            if (answer is None) and self.default_value:
                answer = self.default_value

        return answer

    def parse(self, value):
        return value.strip()

    def get_prompt(self):
        if self.default_value is None:
            return "?"
        else:
            return "[{}] ?".format(self.default_value)


class BooleanSettingDefinition(SettingDefinition):
    def __init__(self, name: str, question: str, guidance: str, default_value=None):
        super().__init__(name, question, guidance, default_value)

    def get_prompt(self):
        if self.default_value is None:
            return "(yes/no) ?"
        else:
            if self.default_value:
                d = "yes"
            else:
                d = "no"
            return "[{}] ?".format(d)

    def parse(self, value):
        if value == "y" or value == "yes":
            return True
        elif value == "n" or value == "no":
            return False
        else:
            return None


definitions = [
    BooleanSettingDefinition("persist_data",
                             "Should data in the database be persisted?",
                             "If you answer no all data will be deleted from the database when Montagu is stopped. Data"
                             " should be persisted for live systems, and not persisted for testing systems.",
                             default_value=True)
]


def load_settings():
    settings = {}

    try:
        with open(path, 'r') as f:
            data = json.load(f) or {}
    except FileNotFoundError:
        data = {}

    for definition in definitions:
        key = definition.name
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

        for definition in missing:
            key = definition.name
            value = definition.ask()
            settings[key] = value

    save_settings(settings)
    return settings


def save_settings(settings):
    with open(path, 'w') as f:
        json.dump(settings, f, indent=4)
