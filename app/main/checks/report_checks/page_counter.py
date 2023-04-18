from ..base_check import BaseReportCriterion, answer


class ReportPageCounter(BaseReportCriterion):
    description = "Проверка количества страниц в файле"
    id = 'page_counter'

    def __init__(self, file_info, min_number=4, max_number=None):
        super().__init__(file_info)
        self.number = [min_number, max_number]

    def check(self):
        count = self.file.page_counter()
        if count >= self.number[0] and (self.number[1] is None or count <= self.number[1]):
            return answer(True, f"Пройдена! В отчете {count} стр.")
        if self.number[1]:
            return answer(False,
                          f'Неверное количество страниц в файле: должно быть [{self.number[0]}, {self.number[1]}] стр. не считая приложения, в отчете {count} стр.')
        else:
            return answer(False,
                          f'Неверное количество страниц в файле: должно быть не менее {self.number[0]} стр. не считая приложения, в отчете {count} стр.')
