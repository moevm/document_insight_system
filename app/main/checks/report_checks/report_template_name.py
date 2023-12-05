import re

from ..base_check import BaseReportCriterion, answer


class ReportTemplateNameCheck(BaseReportCriterion):
    description = "Проверка соответствия названия файла шаблону"
    id = 'report_template_name'

    def __init__(self, file_info, regex="^\d+_[А-Яа-я]+\_[А-Я]{2}_", headers_map=None):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        if headers_map:
            self.reg=regex + headers_map
            self.allowed_name='1111_Иванов_ИИ_NIR2'
        else:
            self.reg = regex + 'ВКР$'
            self.allowed_name = '1111_Иванов_ИИ_ВКР'

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла отчета "<i>{self.filename}</i>" не соответствует шаблону. Допустимый формат:<br>  {self.allowed_name}')
