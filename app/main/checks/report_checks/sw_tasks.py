from logging import getLogger

from ..base_check import BaseReportCriterion, answer

logger = getLogger(__name__)

DEFAULT_CHAPTER = "Введение"
DEFAULT_MIN_TASKS = 3
DEFAULT_MAX_TASKS = 5
DEFAULT_REPORT_TYPE = "VKR"
TASKS_MARKER = "задач" # параграф, с которого начинается перечисление задач
DEFAULT_STOP_MARKERS = [
    "объект",
    "актуальность",
    "цель",
    "предмет",
] # список параграфов, на которых перечисление задач заканчивается


class SWTasksCheck(BaseReportCriterion):
    label = "Проверка количества задач в работе"
    _description = "Проверка на минимальное и максимальное кол-во задач"
    id = "sw_tasks_check"
    warning = True

    def __init__(
        self,
        file_info,
        chapter=DEFAULT_CHAPTER,
        min_tasks=DEFAULT_MIN_TASKS,
        max_tasks=DEFAULT_MAX_TASKS,
        tasks_marker=TASKS_MARKER,
        stop_markers=DEFAULT_STOP_MARKERS,
    ):
        super().__init__(file_info)

        self.chapter = chapter
        self.min_tasks = min_tasks
        self.max_tasks = max_tasks
        self.tasks_marker = tasks_marker
        self.stop_markers = stop_markers

    def check(self):
        chapters = self.file.make_chapters(self.file_type.get('report_type', DEFAULT_REPORT_TYPE))

        tasks = self.find_tasks(chapters)
        if not tasks:
            return answer(False, f'В разделе "{self.chapter}" не обнаружены задачи! 0 Задач.')

        tasks_count = len(tasks)
        if self.min_tasks <= tasks_count <= self.max_tasks:
            return answer(True, "Проверка пройдена!")

        return answer(False, self._wrong_count_verdict(tasks_count))

    def _wrong_count_verdict(self, tasks_count):
        return (
            f"Количество задач исследования должно быть в рамках [{self.min_tasks};{self.max_tasks}],"
            f" сейчас их {tasks_count}."
        )

    def find_tasks(self, chapters):
        """Возвращает список задач, найденных в разделе self.chapter"""
        intro_index = self._find_chapter_index(chapters)
        if intro_index is None:
            return []

        tasks = self._collect_chapter_tasks(chapters[intro_index], started=False)
        if tasks:
            return tasks

        next_chapter = chapters[intro_index + 1] if intro_index + 1 < len(chapters) else None
        if next_chapter and self.tasks_marker in next_chapter['text'].lower():
            return self._collect_chapter_tasks(next_chapter, started=True)

        return []

    def _find_chapter_index(self, chapters):
        for index, chapter in enumerate(chapters):
            if self.chapter.lower() in chapter['text'].lower():
                return index
        return None

    def _collect_chapter_tasks(self, chapter, started):
        """Собирает параграфы главы, идущие после маркера задач и до стоп-маркера"""
        tasks = []
        for paragraph in chapter['child']:
            text = paragraph['text']
            lowered = text.lower().strip()

            if not started:
                if self.tasks_marker in lowered:
                    started = True
                continue

            # стоп-маркер завершает сбор, только если он в начале параграфа
            if any(lowered.startswith(stop) for stop in self.stop_markers):
                break

            if lowered:
                tasks.append(text)

        return tasks
