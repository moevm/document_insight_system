from ._caption_references import CaptionReferences


class ImageReferences(CaptionReferences):
    label = 'Проверка наличия ссылок на все рисунки'
    _description = 'Номера рисунков и ссылок на них должны совпадать.'
    id = 'image_references'
    caption_word = 'Рисунок'
    reference_pattern = r'(?:рис\.|рисун(?:ок|ка|ке|ки|ков|ках))'

    def __init__(self, file_info, image_style='ВКР_Подпись для рисунков'):
        super().__init__(file_info)
        self.caption_style = image_style
