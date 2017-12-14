from .definition import SettingDefinition


class ArraySettingDefinition(SettingDefinition):
    def __init__(self, name: str, question: str, default_value=None):
        super().__init__(name, question, default_value)

    def parse(self, value):
        if len(value) == 0:
            return []

        return value.split(",")
