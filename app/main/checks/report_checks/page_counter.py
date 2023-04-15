from ..base_check import BaseReportCriterion, answer


class ReportPageCounter(BaseReportCriterion):
    description = "Проверка количества страниц в файле"
    id = 'page_counter'

    def __init__(self, file_info, min_number=60, max_number=None):
        super().__init__(file_info)
        self.number = [min_number, max_number]

    def check(self):
        result_str = ''
        count = self.file.page_counter()
        if count >= self.number[0] and (self.number[1] is None or count <= self.number[1]):
            return answer(True, f"Пройдена! В отчете {count} стр не считая Приложения.")
        if self.number[1]:
            result_str += f'Неверное количество страниц в файле: должно быть [{self.number[0]}, {self.number[1]}] стр. не считая приложения, в отчете {count} стр.<br><br>'
        else:
            result_str += f'Неверное количество страниц в файле: должно быть не менее {self.number[0]} стр. не считая приложения, в отчете {count} стр. <br><br>'
        result_str += '''
                    Если количество страниц неверное, попробуйте сделать следующее:
                    <ul>
                        <li>Убедитесь, что заголовок "ПРИЛОЖЕНИЕ А" начинается с первой строки новой страницы PDF-файла;</li>
                        <li>Убедитесь, что для выравнивания заголовка "ПРИЛОЖЕНИЕ А" не использовались пробельные символы или табуляция;</li>
                        <li>Убедитесь в том, что PDF-файл корректно отображает оформление.</li>
                    </ul>
                    '''
        return answer(False, result_str)
