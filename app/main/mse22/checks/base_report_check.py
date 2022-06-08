class BaseReportCheck:
    def __init__(self):
        self.succeeded = True
        self.msg = ""

    def check(self, pages):
        raise NotImplementedError()