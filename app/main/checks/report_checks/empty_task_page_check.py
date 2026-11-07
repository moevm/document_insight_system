import re

from ..base_check import BaseReportCriterion, answer

PAGE_NAME = 'ЗАДАНИЕ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ'


class EmptyTaskPageCheck(BaseReportCriterion):
    label = 'Проверка заполнения страницы с заданием'
    _description = f'Проверяет обязательные поля страницы «{PAGE_NAME}».'
    id = 'empty_task_page_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        pages = self.file.pdf_file.get_text_on_page()
        text = pages.get(2, '')
        if 'задание' not in text.lower():
            return answer(False, f'Страница «{PAGE_NAME}» не найдена на второй странице.')
        text = text.replace('_', ' ')
        labels = ('студент', 'группа', 'руководитель', 'тема работы')
        errors = []
        # Values may share a PDF block, but must not be only the next label.
        for label in labels:
            pattern = re.escape(label) + r'\s*[:—-]?\s*(.+?)(?=' + '|'.join(map(re.escape, labels)) + r'|\n|$)'
            values = re.findall(pattern, text, re.I)
            if not any(re.search(r'[А-Яа-яЁёA-Za-z0-9]', value) for value in values):
                errors.append(label.capitalize())
        dates = re.findall(r'[«"“]?\s*\d{1,2}\s*[»"”]?\s*(?:[А-Яа-яЁё]+|[./]\d{1,2}[./])\s*20\d{2}', text)
        if len(dates) < 2:
            errors.append('Дата выдачи задания / дата представления ВКР к защите')
        return answer(not errors, 'Не заполнены поля: ' + ', '.join(errors) if errors else 'Пройдена!')
