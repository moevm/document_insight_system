from ..base_check import BaseReportCriterion, answer

import app.nlp.text_similarity as ts


class CompareTasksAndContentCheck(BaseReportCriterion):
    label = "Проверка соответствия задач и содержания"
    description = "Степень раскрытия задач в содержании"
    id = 'compare_tasks_and_content_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.tasks = []
        self.chapters = {}
        self.weights = {}
        self.all_to_pass = 0
        self.specific_to_pass = 0
        self.to_ignore = []
        self.minimum_tasks = 0

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
        self.all_to_pass = 0.15
        self.specific_to_pass = 0.05
        self.to_ignore = ["СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ", "ПРИЛОЖЕНИЕ"]
        self.minimum_tasks = 3

    def check(self):
        self.late_init()
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = ""
        possible_tasks = []
        for header in self.headers:
            if header["text"].find("ВВЕДЕНИЕ") >= 0:
                for i, child in enumerate(header["child"]):
                    if child["text"].lower().find("задачи") >= 0:
                        possible_tasks.append(i)
                    if child["text"].lower().find("объект") >= 0 and child["text"].lower().find("исследования") > 0:
                        if not possible_tasks:
                            return answer(False, "В введении не найдены задачи работы")
                        tasks = header["child"][max(possible_tasks) + 1:i]
                        while len(tasks <= self.minimum_tasks):
                            try:
                                possible_tasks.remove(max(possible_tasks))
                                tasks = header["child"][max(possible_tasks) + 1:i]
                            except:
                                return answer(False, f"В введении меньше {self.minimum_tasks} задач, что меньше необходимого минимума")
                        self.tasks = [task["text"] for task in tasks]
                        break
            if any(ignore_phrase in header["text"] for ignore_phrase in self.to_ignore):
                continue
            text = ""
            for child in header["child"]:
                text += child['text']
            self.chapters[header["text"]] = text
        self.chapters = {k: v for k, v in self.chapters.items() if v and v.strip()}
        NLPProcessor = ts.NLPProcessor()
        all_tasks_result = NLPProcessor.calculate_cosine_similarity(" ".join(self.tasks), self.chapters)
        max_result = max(all_tasks_result.values())
        for k, v in all_tasks_result.items():
            for chapter, weight in self.weights.items():
                if k.find(chapter) == 0:
                    all_tasks_result[k] = v * weight
                    break
            all_tasks_result[k] = round(all_tasks_result[k] / max_result, 3)
        avg = round(sum(all_tasks_result.values()) / len(all_tasks_result.values()), 3)
        if avg < self.all_to_pass:
            return answer(False, f"Задачи недостаточно раскрыты в содержании (нужно {self.all_to_pass * 100}%, набрано {avg * 100}%)")
        result += f"<br><b>Задачи раскрыты на {avg * 100}%</b><br>"
        for task in self.tasks:
            cur_task = NLPProcessor.calculate_cosine_similarity(task, self.chapters)
            max_result = max(cur_task.values())
            for k, v in cur_task.items():
                for chapter, weight in self.weights.items():
                    if k.find(chapter) == 0:
                        cur_task[k] = v * weight
                        break
                cur_task[k] = cur_task[k] / max_result
            sorted_chapters = dict(sorted(cur_task.items(), key=lambda item: item[1], reverse=True))
            specific_avg = sum(sorted_chapters.values()) / len(sorted_chapters.values())
            specific_avg = round(specific_avg, 3)
            if specific_avg < self.specific_to_pass:
                return answer(False, f"<br>Задача \"{task}\" недостаточно раскрыта<br>")
            result += f"<br><b>Задача \"{task}\" раскрыта на {round(specific_avg * 100, 2)}%</b><br><br>Задачу \"{task}\" наиболее раскрывают разделы: <br>"
            for i, key in enumerate(sorted_chapters.keys()):
                if i >= 3:
                    break
                result += f"<br>\"{key}\", {round(self.__output(sorted_chapters[key], sum(sorted_chapters.values())), 3)}% текста раскрывают задачу<br>"
        all_tasks_result = dict(sorted(all_tasks_result.items(), key=lambda item: item[1], reverse=True))
        result += f"<br><b>Разделы, наименее раскрывающие задачи:</b><br>"
        for i, key in enumerate(all_tasks_result.keys()):
            if i < len(all_tasks_result.keys()) - 5:
                continue
            result += f"<br>{key}: {round(all_tasks_result[key] * 100, 3)}%<br>"
        return answer(True, result)

    def __output(self, value, summ):
        return (value / summ) * 100
