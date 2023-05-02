from ..base_check import BaseReportCriterion, answer


class ReportPageCounter(BaseReportCriterion):
    description = "Проверка количества страниц в файле"
    id = 'page_counter'
    priority = True

    def __init__(self, file_info, min_number=50, max_number=None):
        super().__init__(file_info)
        self.number = [min_number, max_number]

    def check(self):
        result_str = ''
        count = self.file.page_counter()
        if count >= self.number[0] and (self.number[1] is None or count <= self.number[1]):
            return answer(True, f"Пройдена! В отчете {count} стр не считая Приложения. <br>"
                                f"Последняя учтенная страница {self.format_page_link([self.file.count])}.")
        if self.number[1]:
            result_str += f'Неверное количество страниц в файле: должно быть [{self.number[0]}, {self.number[1]}] ' \
                          f'стр. не считая приложения, в отчете {count} стр. <br>Последняя учтенная страница ' \
                          f'{self.format_page_link([self.file.count])}.<br><br>'
        else:
            result_str += f'Неверное количество страниц в файле: должно быть не менее {self.number[0]} стр. ' \
                          f'не считая приложения, в отчете {count} стр. <br>Последняя учтенная страница ' \
                          f'{self.format_page_link([self.file.count])}.<br><br>'
        result_str += '''
                    Если количество страниц неверное, попробуйте сделать следующее:
                    <ul>
                        <li>Убедитесь, что заголовок "ПРИЛОЖЕНИЕ А" начинается с первой строки новой страницы PDF-файла;</li>
                        <li>Убедитесь, что для заголовок "ПРИЛОЖЕНИЕ А" имеет стиль "Заголовок 2,ВКР_Заголовок 2";</li>
                        <li>Убедитесь, что PDF-файл корректно отображает оформление.</li>
                    </ul>
                    '''
        result_str += f"Если сгенерированный PDF-файл имеет проблемы с оформлением, попробуйте загрузить свой PDF."
        return answer(False, result_str)
