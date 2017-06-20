class SettingDefinition:
    def __init__(self, name: str, question: str, guidance: str=None, default_value=None, first_time_only=False):
        self.name = name
        self.question = question
        self.guidance = guidance
        self.default_value = default_value
        self.first_time_only = first_time_only

    def ask(self):
        print("")
        print(self.question)
        self.print_guidance()
        answer = None
        prompt = self.get_prompt() + " "

        while answer is None:
            answer = self.parse(input(prompt))
            if (answer is None or str(answer).strip() == "") and self.default_value:
                answer = self.default_value

        return answer

    def print_guidance(self):
        if self.guidance:
            print(self.guidance)

    def parse(self, value):
        return value.strip()

    def get_prompt(self):
        if self.default_value is None:
            return "?"
        else:
            return "[{}] ?".format(self.default_value)
