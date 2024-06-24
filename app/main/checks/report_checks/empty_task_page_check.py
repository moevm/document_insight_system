from ..base_check import BaseReportCriterion, answer

PAGE_NAME = "ЗАДАНИЕ НА ВЫПУСКНУЮ КВАЛИФИКАЦИОННУЮ РАБОТУ"


class EmptyTaskPageCheck(BaseReportCriterion):
    label = "Проверка на пустоту страницы с заданием"
    description = f'Страница "{PAGE_NAME}" должна содержать текст'
    id = 'empty_task_page_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        rows_text = self.file.pdf_file.page_rows_text(1)
        print(rows_text)
        if 'ЗАДАНИЕ' not in rows_text[0][4]:
            return answer(False, f'Страница "{PAGE_NAME}" не найдена. Убедитесь, что она является второй в документе и не содержит ошибок в заголовке.')
        elif len(rows_text) < 4:
            return answer(False, f'Страница "{PAGE_NAME}" не содержит текста.')
        else:
            result = {"студент", 'темаработы', 'руководитель'}
            check_words = {"студент", 'темаработы', 'руководитель'}
            for k in check_words:
                for row in rows_text:
                    row_string = row[4].replace('\n', '').replace(' ', '').replace('_', '').lower()
                    if k in row_string:
                        clear_row_string = row_string.replace(k, '')
                        if len(clear_row_string) > 2:
                            result.discard(k)
            if not result:
                return answer(True, 'Пройдена!')
            else:
                return answer(False, f'Некоторые необходимые поля пусты или отсутствуют. Проверьте: {result}')
