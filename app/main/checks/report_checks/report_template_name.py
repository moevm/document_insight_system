import re

from ..base_check import BaseReportCriterion, answer


class ReportTemplateNameCheck(BaseReportCriterion):
    description = "Проверка соответствия названия файла шаблону"
    id = 'report_template_name'
        # Шаблон: Номер группы_Фамилия_Инициалы_NIR2

    def __init__(self, file_info, regex="^\d+_[А-Яа-я]+\_[А-Я]{2}_NIR2$"):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.reg = regex

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла отчета "<i>{self.filename}</i>" не соответствует шаблону. Допустимый формат:<br>   1010_ИВАНОВ_ИИ_NIR2')
