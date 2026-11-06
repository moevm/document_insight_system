from ._caption_references import CaptionReferences


class TableReferences(CaptionReferences):
    label = 'Проверка наличия ссылок на все таблицы'
    _description = 'Номера таблиц и ссылок на них должны совпадать.'
    id = 'table_references'
    caption_word = 'Таблица'
    reference_pattern = r'(?:табл\.|таблиц(?:а|е|у|ы|ах))'

    def __init__(self, file_info, table_style='ВКР_Подпись таблицы'):
        super().__init__(file_info)
        self.caption_style = table_style
