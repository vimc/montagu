from typing import List, Tuple

from .definition import SettingDefinition


class EnumSettingDefinition(SettingDefinition):
    def __init__(self, name: str, question: str, options: List[Tuple[str, str]],
                 default_value=None,
                 first_time_only=False):
        super().__init__(name, question, "", default_value, first_time_only)
        self.full_options = options
        self.options = [key for key, description in options]

    def parse(self, value):
        value = super().parse(value)
        if value not in self.options:
            print("Please choose from these options: {}".format(self.options))
            return None
        return value

    def print_guidance(self):
        print("Options:")
        for key, description in self.full_options:
            print("- {key}: {description}".format(key=key,
                                                  description=description))
