from ..base_check import BaseReportCriterion, answer

SYMBOLS_SET = ['%', '1']
MAX_SYMBOLS_PERCENTAGE = 0
MAX_TEXT_DENSITY = 4

class ImageTextCheck(BaseReportCriterion):
    label = "Проверка текста, считанного с изображений"
    description = ''
    id = 'image_text_check'
    # Подобрать значения для symbols_set, max_symbols_percentage, max_text_density
    def __init__(self, file_info, symbols_set=['%', '1'], max_symbols_percentage=0, max_text_density=4):
        super().__init__(file_info)
        self.images = self.file.images
        self.symbols_set = symbols_set
        self.max_symbols_percentage = max_symbols_percentage
        self.max_text_density = max_text_density

    def check(self):
        if self.images:
            return answer(True, 'Изображения проверяются!')
        else:
            return answer(True, 'Изображения не найдены!')
