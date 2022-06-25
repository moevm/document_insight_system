from ..base_check import BaseCheck, answer


class ReportSimpleCheck(BaseCheck):
    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        if self.file.paragraphs:
            return answer(True, "Пройдена!")
        else:
            return answer(False, f'Количество paragraphs в файле = 0')
