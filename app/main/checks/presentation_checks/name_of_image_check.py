from ..base_check import BasePresCriterion, answer
from app.utils.parse_for_html import format_header

class PresImageCaptureCheck(BasePresCriterion):
    label = "Проверка наличия подписи к рисункам"
    description = 'Подписи к рисункам должны содержать слово "Рисунок". Подпись к рисункам на слайдах без текста необязательна'
    id = 'pres_image_capture'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        slides_without_capture = set()
        slide_with_image_only = set()
        result_str = 'Не пройдена! '
        all_captions = []
        for num, slide in enumerate(self.file.slides, 1):
            captions = slide.get_captions()
            if captions:
                for caption in captions:
                    body_text = slide.get_text().replace(captions[0][0], '').replace(slide.get_title(), '').replace('<number>', '').replace(' ', '')
                    if body_text.strip() or slide.get_table():
                        all_captions.append(caption[0])
                        if 'Рисунок' not in caption[0]:
                            slides_without_capture.add(num)
                    else:
                        if caption[0] != slide.get_title():
                            slide_with_image_only.add(num)
        if slides_without_capture:
            result_str += format_header(
                'Подписи к рисункам на следующих слайдах отсутствуют или не содержат слова "Рисунок": {}'.format(
                        ', '.join(self.format_page_link(sorted(slides_without_capture)))))
        if slide_with_image_only:
            result_str += format_header(
                'Подписи к рисункам на следующих слайдах без текста необязательны: {}'.format(
                        ', '.join(self.format_page_link(sorted(slide_with_image_only)))))
        if result_str:
            return answer(False, result_str + f'Список всех обнаруженных подписей: {", ".join(all_captions)}')
        else:
            return answer(True, 'Пройдена!')
