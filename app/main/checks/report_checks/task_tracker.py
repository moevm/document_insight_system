import re

from app.main.reports.section_patterns import INTRODUCTION_TITLE

from ..base_check import BaseReportCriterion, answer, morph


class ReportTaskTracker(BaseReportCriterion):
    label = "Проверка количества задач и их недопустимости"
    _description = 'Не пропускать задачи из серии "доделать, решить, описать" и проверить количество задач'
    id = 'report_task_tracker'

    def __init__(
        self,
        file_info,
        chapter=INTRODUCTION_TITLE,
        patterns=('задач', 'объект'),
        deny_list=('доделать', 'решить', 'описать'),
        min_count_tasks=1,
        max_count_tasks=3,
    ):
        super().__init__(file_info)
        self.chapter = chapter
        self.chapters = []
        self.patterns = patterns
        if len(patterns) != 2:
            raise ValueError("patterns должен содержать начальный и конечный маркер задач.")
        self.deny_list = [morph.parse(word)[0].normal_form for word in deny_list]
        self.min_count_tasks = min_count_tasks
        self.max_count_tasks = max_count_tasks

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if not self.has_enough_pages():
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        tasks = self.find_tasks()

        if not tasks and self.min_count_tasks > 0:
            return answer(False, f"Не обнаружен раздел '{self.chapter}' или не обнаружены задачи")

        if not (self.min_count_tasks <= len(tasks) <= self.max_count_tasks):
            return answer(
                False,
                f"Найдено: {len(tasks)} задач. "
                + f"Количество задач должно быть в диапазоне [{self.min_count_tasks};{self.max_count_tasks}].",
            )

        word_in_docs = []
        for task in tasks:
            for word in task:
                normal_form = morph.parse(word)[0].normal_form
                if normal_form in self.deny_list:
                    word_in_docs.append(word)
        if word_in_docs:
            return answer(
                False, f'Задачи не должны содержать слова: {self.deny_list}! Обнаруженные слова: {word_in_docs}.'
            )
        else:
            return answer(True, 'Задачи сформулированы корректно!')

    def find_tasks(self):  # TODO: fix problem w/sequences
        intro = None
        tasks = []
        for header in self.chapters:
            if header["text"].lower().find(self.chapter.lower()) >= 0:
                intro = header
                break
        if not intro:
            return tasks

        coef = float('inf')
        for i in range(len(intro["child"])):
            text = intro["child"][i]["text"].lower()
            if self.patterns[1] in text:
                return tasks
            if self.patterns[0] in text:
                coef = i
            if i > coef:
                words = [word for word in text.split() if word.strip()]
                if words:
                    tasks.append(re.findall(r'\w+(?:-\w+)*', text))
        return tasks
