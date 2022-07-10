import re

from ..base_check import BaseReportCriterion, answer


class ReportNumberOfPages(BaseReportCriterion):
    description = "Проверка количества страниц в файле"
    id = 'page_counter'

    def __init__(self, file_info, minNumber=0, maxNumber=None):
        super().__init__(file_info)

        self.minNumber = minNumber
        self.maxNumber = maxNumber

    def check(self):
        count = 0
        for k, v in self.file.pdf_file.text_on_page.items():
            if re.search('приложение [а-я][\n .]', v.lower()):
                break
            count += 1

        if count >= self.minNumber and (self.maxNumber is None or count <= self.maxNumber):
            return answer(True, f"Пройдена! {count} стр.")
        if self.maxNumber:
            return answer(False,
                          f'Неверное количество страниц в файле: должно быть [{self.minNumber}, {self.maxNumber}] стр., в отчете {count} стр.')
        else:
            return answer(False,
                          f'Неверное количество страниц в файле: должно быть не менее {self.minNumber} стр., в отчете {count} стр.')
