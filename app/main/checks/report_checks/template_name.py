import re
from datetime import datetime

from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer

CUR_YEAR = datetime.now().year


class ReportTemplateNameCheck(BaseReportCriterion):
    label = "Проверка соответствия названия файла шаблону"
    description = f'Шаблон названия зависит от типа работы, например: "{CUR_YEAR}ВКР111111ИВАНОВ", "1111_Иванов_ИИ_NIR2"'
    id = 'template_name'

    def __init__(self, file_info, headers_map=None):
        super().__init__(file_info)
        self.filename = self.filename.split('.', 1)[0]
        self.template_name = ''
        if headers_map:
            self.config = headers_map
        else:
            self.config = 'VKR_HEADERS'
            self.regex = str(CUR_YEAR)+'ВКР[0-9]{6}([А-ЯЁ]+)'
            self.template_name = (self.regex, f'{CUR_YEAR}ВКР030301ИВАНОВ')

    def late_init(self):
        self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
        if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config):
            self.template_name = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['template_name']
        else:
            if 'any_header' in StyleCheckSettings.CONFIGS.get(self.config):
                self.template_name = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['template_name']

    def check(self):
        if not self.template_name:
            self.late_init()
        if re.fullmatch(self.template_name[0], self.filename):
            return answer(True, "Пройдена!")
        else:
            return answer(False,
                          f'Название файла отчета "<i>{self.filename}</i>" не соответствует шаблону (Пример: {self.template_name[1]})')
