def answer(mod, value, *args):
    return {
        'pass': bool(mod),
        'value': value,
        'verdict': (args)
    }

class BaseCheck:
    def __init__(self, presentation):
        self.presentation = presentation

    def check(self):
        raise NotImplementedError()
