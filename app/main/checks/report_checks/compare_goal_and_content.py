from ..base_check import BaseReportCriterion, answer

import app.nlp.text_similarity as ts


class CompareGoalAndContentCheck(BaseReportCriterion):
    description = "Проверка соответствия цели и содержания"
    id = 'compare_goal_and_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.goal = ""
        self.chapters = {}
        self.weights = {}
        self.to_pass = 0
        self.to_ignore = []

    def late_init(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.weights = {
            "ВВЕДЕНИЕ": 1,
            "1": 2,
            "2": 2,
            "3": 5,
            "4": 2,
            "5": 1,
            "ЗАКЛЮЧЕНИЕ": 1
        }
        self.to_pass = 0.1
        self.to_ignore = ["СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "ПРИЛОЖЕНИЕ"]

    def check(self):
        self.late_init()
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = ""
        intro_text = ""
        for header in self.headers:
            if header["text"] == "ВВЕДЕНИЕ":
                for child in header["child"]:
                    intro_text += child["text"]
        goal_index = intro_text.find("Цель")
        if goal_index > 0:
            goal_start = goal_index + len("Цель") + 1
            goal_end = intro_text.find(".", goal_start)
            self.goal = intro_text[goal_start:goal_end]
        else:
            return answer(False, "В введении не найдена цель работы")
        for header in self.headers:
            if any(ignore_phrase in header["text"] for ignore_phrase in self.to_ignore):
                continue
            text = ""
            for child in header["child"]:
                text += child['text']
            self.chapters[header["text"]] = text
        self.chapters = {k: v for k, v in self.chapters.items() if v and v.strip()}
        NLPProcessor = ts.NLPProcessor()
        calculate_result = NLPProcessor.calculate_cosine_similarity(self.goal, self.chapters)
        max_result = max(calculate_result.values())
        for k, v in calculate_result.items():
            for chapter, weight in self.weights.items():
                if k.find(chapter) == 0:
                    calculate_result[k] = v * weight
                    break
            calculate_result[k] = calculate_result[k] / max_result
        avg = round(sum(calculate_result.values()) / len(calculate_result.values()), 3)
        if avg < self.to_pass:
            return answer(False,
                          f"Цель недостаточно раскрыта в содержании (нужно {self.to_pass * 100}%, набрано {avg * 100}%)")
        result += f"<br><b>Тема раскрыта на {avg * 100}%</b><br>"
        sorted_chapters = dict(sorted(calculate_result.items(), key=lambda item: item[1], reverse=True))
        result += f"<br><b>7 разделов, наиболее раскрывающих тему:</b><br>"
        for i, key in enumerate(sorted_chapters.keys()):
            if i >= 7:
                break
            result += f"<br>\"{key}\", {round(self.__output(sorted_chapters[key], sum(sorted_chapters.values())), 3)}% текста раскрывают тему<br>"
        result += f"<br><b>7 разделов, наименее раскрывающих тему:</b><br>"
        for i, key in enumerate(sorted_chapters.keys()):
            if i < len(sorted_chapters) - 7:
                continue
            result += f"<br>\"{key}\", {self.__output(sorted_chapters[key], sum(sorted_chapters.values()))}% текста раскрывают тему<br>"
        return answer(True, result)

    def __output(self, value, summ):
        return round(value / summ, 3) * 100
