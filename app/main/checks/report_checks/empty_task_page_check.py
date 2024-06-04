from ..base_check import BaseReportCriterion, answer

PAGE_NAME = "ЗАДАНИЕ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ"
TASK_PATTERN = "заданиенавыпускнуюквалификационнуюработу"

class EmptyTaskPageCheck(BaseReportCriterion):
    label = "Проверка на пустоту страницы с заданием"
    description = f'Страница "{PAGE_NAME}" должна содержать текст'
    id = 'empty_task_page_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        task_page = self.file.pdf_file.text_on_page[2]
        task_page_string  = task_page.replace('\n', ' ').replace(' ', '').lower()
        if TASK_PATTERN not in task_page_string:
            return answer(False, f'Страница "{PAGE_NAME}" не найдена. Убедитесь, что она является второй в документе и не содержит ошибок в заголовке.')
        task_page_without_head = task_page_string.replace(TASK_PATTERN, '')
        if len(task_page_without_head) > 1: #not 0 because of page number
            return answer(True, 'Пройдена!')
        else:
            return answer(False, f'Страница "{PAGE_NAME}" не содержит текста.')
