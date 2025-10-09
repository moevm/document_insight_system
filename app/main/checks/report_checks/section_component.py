from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportSectionComponent(BaseReportCriterion):
    label = "Проверка наличия необходимых компонентов указанного раздела"
    description = "Проверка наличия необходимых компонентов указанного раздела"
    id = 'report_section_component'

    def __init__(self, file_info, chapter='Введение', patterns=('цель', 'задач', 'объект', 'предмет'), headers_map = None):
        super().__init__(file_info)
        self.intro = {}
        if headers_map:
            self.config = headers_map
            self.chapter = ''
            patterns = ('цель', 'задач')
        else:
            self.chapter = chapter
        self.chapters = []
        self.patterns = []
        for pattern in patterns:
            self.patterns.append({"name": pattern.capitalize(), "text": pattern, "marker": 0})

    def late_init(self):
        if not self.chapter:
            self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
            if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config):
                self.chapter = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]["header_for_report_section_component"]
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        if not self.chapter:
            return answer(True, f'Данная проверка не предусмотрена для работы с темой "{self.headers_main}"')
        result_str = ''
        for intro in self.chapters:
            header = intro["text"].lower()
            if header.find(self.chapter.lower()) >= 0:
                self.intro = intro
                break

        if self.intro:
            for intro_par in self.intro["child"]:
                par = intro_par["text"].lower()
                for i in range(len(self.patterns)):
                    if par.find(self.patterns[i]["text"]) >= 0:
                        self.patterns[i]["marker"] = 1
        else:
            return answer(0, f'Раздел "{self.chapter}" не обнаружен!')

        for pattern in self.patterns:
            if not pattern["marker"]:
                result_str += '<li>' + pattern["name"] + '</li>'

        if not result_str:
            return answer(True, f'Все необходимые компоненты раздела "{self.chapter}" обнаружены!')
        else:
            return answer(False,
                          f'Не найдены следующие компоненты раздела {self.chapter} (обратите внимание на требования к разделу и его составляющим): <ul>{result_str}</ul>')
