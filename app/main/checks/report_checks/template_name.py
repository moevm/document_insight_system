import re

from ..base_check import BasePresCriterion, answer


class TemplateNameCheck(BaseReportCriterion):
    description = "Проверка соответствия названия файла шаблону"
    id = 'template_name_report'
        # Шаблон: НОМЕР_ГРУППЫ-Фамилия_ИНИЦИАЛЫ

    def __init__(self, file_info, regex="^\d+-[А-Яа-яЁё]+\_[А-Яа-яЁё]\.[А-Яа-яЁё]\.$"):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.reg = regex

    def check(self):
        if re.fullmatch(self.reg, self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла отчета "<i>{self.filename}</i>" не соответствует шаблону. Допустимый формат:<br>   171_Иванов_И.И.')
