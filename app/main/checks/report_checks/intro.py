from ..base_check import BaseReportCriterion, answer


class ReportIntroduction(BaseReportCriterion):
    description = "Проверка наличия необходимых компонент раздела Введение"
    id = 'introduction_word_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.intro = {}
        self.patterns = [{"name": "Цель", "text": "цель","marker": 0}, {"name": "Задачи", "text": "задачи", "marker": 0}, {"name": "Объект", "text": "объект", "marker": 0}, {"name": "Предмет", "text": "предмет", "marker": 0}, {"name": "Практическая(ую) ценность работы", "text": "практическ", "marker": 0}]

    def check(self):
        result_str = ''
        headers = self.file.make_chapters(self.file_type['report_type'])
        for intro in self.file.chapters:
            header = intro["text"].lower()
            if header.find('введение') >= 0:
                self.intro = intro
                break

        if self.intro:
            for intro_par in self.intro["child"]:
                par = intro_par["text"].lower()
                for i in range(len(self.patterns)):
                    if par.find(self.patterns[i]["text"]) >= 0:
                        self.patterns[i]["marker"] = 1
        else:
            return answer(0, "Раздел Введение не обнаружен!")

        for pattern in self.patterns:
            if not pattern["marker"]:
                result_str += '</li><li>'+ pattern["name"]

        result_score = 0
        if len(result_str) == 0:
            result_score = 1
        if result_score:
            return answer(result_score, "Все необходимые компоненты раздела Введение обнаружены!")
        else:
            return answer(result_score,
                          f'Не найдены следующие компоненты Введения: <ul><li>{result_str}</ul>')