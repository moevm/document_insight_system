from ..base_check import BaseReportCriterion, answer, morph
from .style_check_settings import StyleCheckSettings


class ReportTaskTracker(BaseReportCriterion):
    label = "Поиск недопустимых задач"
    description = 'Не пропускать задачи из серии "доделать, решить, описать"'
    id = 'report_task_tracker'

    def __init__(self, file_info, chapter='Введение', patterns=('задач', 'объект'), deny_list=['доделать', 'решить', 'описать']):
        super().__init__(file_info)
        self.chapter = chapter
        self.chapters = []
        self.patterns = patterns
        self.deny_list = [morph.parse(word)[0].normal_form for word in deny_list]

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        tasks = self.find_tasks()
        if not tasks:
            return answer(False, f'Раздел "{self.chapter}" не обнаружен!')
        word_in_docs = []
        for task in tasks:
            for word in task:
                normal_form = morph.parse(word)[0].normal_form
                if normal_form in self.deny_list:
                    word_in_docs.append(word)
        if word_in_docs:
            return answer(False, f'Задачи не должны содержать слова: {self.deny_list}! Обнаруженные слова: {word_in_docs}.')
        else:
            return answer(True, 'Задачи сформулированы корректно!')

    def find_tasks(self):
        intro = None
        tasks = []
        for header in self.chapters:
            if header["text"].lower().find(self.chapter.lower()) >= 0:
                intro = header
        if intro:
            coef = float('inf')
            for i in range(len(intro["child"])):
                text = intro["child"][i]["text"].lower()
                if self.patterns[1] in text:
                    return tasks
                if self.patterns[0] in text:
                    coef= i
                if i > coef:
                    words = [word for word in text.split() if word.strip()]
                    if words:
                        tasks.append(text.split())
        return tasks
            
