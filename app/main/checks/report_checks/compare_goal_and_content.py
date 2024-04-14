from ..base_check import BaseReportCriterion, answer

import app.nlp.text_similarity as ts


class CompareGoalAndContentCheck(BaseReportCriterion):
    description = "Проверка соответствия цели и содержания"
    id = 'compare_goal_and_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.goal = ""
        self.tasks = []
        self.main_text = []
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
        self.to_pass = 0.15
        self.to_ignore = ["СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"]

    def check(self):
        self.late_init()
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = ""
        for text_on_page in self.file.pdf_file.get_text_on_page().values():
            if text_on_page.split()[0].lower() != "введение":
                continue
            goal_index = text_on_page.find("Цель")
            tasks_index = text_on_page.find("Задачи")
            if goal_index != -1 and tasks_index != -1:
                goal_start = goal_index + len("Цель") + 1
                goal_end = tasks_index
                self.goal = text_on_page[goal_start:goal_end].strip()
                tasks_start = tasks_index + len("Задачи") + 1
                tasks_end = text_on_page.find(".", tasks_start)
                self.tasks = text_on_page[tasks_start:tasks_end].split(';')
            elif goal_index == -1:
                return answer(False, "В введении не написана цель работы")
            elif tasks_index == -1:
                return answer(False, "В введении не написаны задачи")
        for header in self.headers:
            if header["text"] in self.to_ignore:
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
                if 0 <= k.find(chapter) < 1:
                    calculate_result[k] = v * weight
                    break
            calculate_result[k] = calculate_result[k] / max_result
        avg = sum(calculate_result.values()) / len(calculate_result.values())
        result += f"<br>Средняя схожесть текста с темой: {avg}<br>"
        sorted_chapters = dict(sorted(calculate_result.items(), key=lambda item: item[1], reverse=True))
        result += f"<br>7 глав, наиболее раскрывающих тему:<br>"
        for i, key in enumerate(sorted_chapters.keys()):
            if i >= 7:
                break
            result += f"<br>Для главы \"{key}\" схожесть составила {sorted_chapters[key]}<br>"
        result += f"<br>7 глав, наименее раскрывающих тему:<br>"
        for i, key in enumerate(sorted_chapters.keys()):
            if i < len(sorted_chapters) - 7:
                continue
            result += f"<br>Для главы \"{key}\" схожесть составила {sorted_chapters[key]}<br>"
        if avg < self.to_pass:
            return answer(False, f"Цель недостаточно раскрыта в содержании (нужно {self.to_pass}, набрано {avg})")
        return answer(True, result)
