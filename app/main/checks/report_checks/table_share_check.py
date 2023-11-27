from ..base_check import BaseReportCriterion, answer


class ReportTableShareCheck(BaseReportCriterion):
    description = "Проверка доли объема отчёта, приходящейся на таблицы"
    id = 'table_share_check'

    def __init__(self, file_info, limit=0.3):
        super().__init__(file_info)
        self.limit = limit

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        
        table_height = 0
        total_table_height = 0
        for table in self.file.tables:
            print(9999999999)
            print(table)
            for row in table.rows:
                if row.height is not None:
                    table_height += row.height
            total_table_height += table_height # in points

        if len(self.file.file.sections):
            available_space = self.file.file.sections[0].page_height - self.file.file.sections[0].bottom_margin - \
                              self.file.file.sections[0].top_margin # in points
            table_pages = total_table_height / available_space
            share = table_pages / self.file.count
            if share == 0:
                return answer(False, "Не удалось посчитать размер таблиц. Проверьте правильность оформления таблиц.")
            if share > self.limit:
                result_str = f'Проверка не пройдена! Таблицы в работе занимают около {round(share, 2)} объема ' \
                             f'документа без учета приложения, ограничение - {round(self.limit, 2)}'
                result_str += '''
                            Если доля отчета, приходящаяся на таблицы, больше нормы, попробуйте сделать следующее:
                            <ul>
                                <li>Попробуйте перенести малозначимые таблицы в Приложение;</li>
                                <li>Если у вас уже есть раздел Приложение, убедитесь, что количество страниц в отчете посчитано программой без учета приложения;</li>
                                <li>Если страницы посчитаны программой неверно, убедитесь, что заголовок приложения правильно оформлен;</li>
                                <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
                            </ul>
                            '''
                return answer(False, result_str)
            else:
                return answer(True, f'Пройдена!')
        return answer(False, 'Во время обработки произошла критическая ошибка')
