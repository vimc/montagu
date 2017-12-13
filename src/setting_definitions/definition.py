class SettingDefinition:
    def __init__(self, name: str,
                 question: str,
                 guidance: str = None,
                 default_value=None,
                 first_time_only=False,
                 is_required=None):
        """If is_required is not specified, the question will always be asked. Alternatively,
        it can be a function that takes a dictionary of settings gathered so far and returns
        True (meaning this question needs to be asked) or False (meaning, skip this question)"""
        self.name = name
        self.question = question
        self.guidance = guidance
        self.default_value = default_value
        self.first_time_only = first_time_only
        self._is_required = is_required
        if first_time_only:
            raise Exception("Don't use first_time_only")

    def ask(self):
        print("")
        print(self.question)
        self.print_guidance()
        answer = None
        prompt = self.get_prompt() + " "

        while answer is None:
            try:
                answer = self.parse(input(prompt))
            except Exception as e:
                print("Unable to get value for {}".format(self.name))
                raise
            if (answer is None or str(answer).strip() == "") and (self.default_value is not None):
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

    def is_required(self, settings_so_far):
        if self._is_required:
            return self._is_required(settings_so_far)
        else:
            return True
