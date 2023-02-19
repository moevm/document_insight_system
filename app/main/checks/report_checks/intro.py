from ..base_check import BaseReportCriterion, answer


class ReportIntroduction(BaseReportCriterion):
    description = "Проверка наличия необходимых компонент раздела Введение"
    id = 'introduction_word_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.intro = {}
        self.patterns = [{"text": "Цель", "marker": 0}, {"text": "Задачи", "marker": 0}, {"text": "Предмет", "marker": 0}, {"text": "Объект", "marker": 0}, {"text": "Практическую ценность работы", "marker": 0}]

    def check(self):
        result_str = ''
        chapters = self.file.make_chapters(self.file_type['report_type'])
        for intro in self.file.chapters:
            header = intro["text"].lower()
            if header.find('введение') >= 0:
                self.intro = intro
                break

        if self.intro:
            for intro_par in self.intro["child"]:
                par = intro_par["text"].lower()
                for i in range(len(self.patterns)):
                    if par.find(self.patterns[i]["text"].lower()) >= 0:
                        self.patterns[i]["marker"] = 1
        else:
            return answer(0, "Раздел Введение не обнаружен!")

        for pattern in self.patterns:
            if not pattern["marker"]:
                result_str = '</li><li>'.join(pattern["text"])

        result_score = 0
        if not len(result_str):
            result_score = 1
        if result_score:
            return answer(result_score, "Все необходимые компоненты раздела Введение обнаружены!")
        else:
            return answer(result_score,
                          f'Не найдены следующие компоненты Введения: <ul><li>{result_str}</ul>')
