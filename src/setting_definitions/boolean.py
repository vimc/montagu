from .definition import SettingDefinition


class BooleanSettingDefinition(SettingDefinition):
    def __init__(self, name: str, question: str, guidance: str,
                 default_value=None):
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
