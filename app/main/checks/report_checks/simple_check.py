from app.main.checks.base_check import BaseCheck, answer


class ReportSimpleCheck(BaseCheck):
    def __init__(self, file):
        super().__init__(file)

    def check(self):
        if self.file.paragraphs:
            return answer(True, "Пройдена!")
        else:
            return answer(False, f'Количество paragraphs в файле = 0')
