import re
from ..base_check import BaseReportCriterion, answer

PAGE_NAME = "ЗАДАНИЕ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ"


class EmptyTaskPageCheck(BaseReportCriterion):
    label = "Проверка на пустоту страницы с заданием"
    description = f'Страница "{PAGE_NAME}" должна содержать текст'
    id = 'empty_task_page_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.check_words = {'студент', 'руководитель', 'тема работы'}
        self.check_first_pattern = r'^студент+[а-яА-ЯёЁa-zA-Z]+группа\d+$'
        self.check_date_pattern = r'^«\d+»[а-яА-ЯёЁa-zA-Z]+20\d+г«\d+»[а-яА-ЯёЁa-zA-Z]+20\d+г$'
        self.result = {'Cтудент, Группа', 'Дата выдачи задания, Дата представления ВКР к защите', 'Студент', 'Руководитель', 'Тема работы'}

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        rows_text = self.file.pdf_file.page_rows_text(1)
        if 'ЗАДАНИЕ' not in rows_text[0][4]:
            return answer(False, f'Страница "{PAGE_NAME}" не найдена. Убедитесь, что она является второй в документе и не содержит ошибок в заголовке.')
        elif len(rows_text) < 4:
            return answer(False, f'Страница "{PAGE_NAME}" не содержит текста.')
        else:
            start_string = 0
            for row in rows_text:
                row_string = row[4].replace('\n', '').replace('.', '').replace(' ', '').replace('_', '').lower()
                if re.match(self.check_first_pattern, row_string):
                    self.result.discard('Cтудент, Группа')
                    start_string = row[5]
                if re.match(self.check_date_pattern, row_string):
                    self.result.discard('Дата выдачи задания, Дата представления ВКР к защите')
            for k in self.check_words:
                for row in rows_text[start_string+1:]:
                    row_string = row[4].replace('\n', '').replace(' ', '').replace('_', '').lower()
                    if k.replace(' ', '') in row_string:
                        if len(row_string) > (len(k)+2):
                            self.result.discard(k.capitalize())
            if not self.result:
                return answer(True, 'Пройдена!')
            else:
                return answer(False, f'Некоторые необходимые поля пусты или отсутствуют. Проверьте поля: «{"», «".join(self.result)}»')
