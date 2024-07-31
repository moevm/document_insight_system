from ..base_check import BasePresCriterion, answer


class PresImageNameCheck(BasePresCriterion):
    label = "Проверка наличия подписи к рисункам"
    description = ''
    id = 'pres_image_name'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        wrong_slide = []
        for num, slide in enumerate(self.file.slides, 1):
            count_image = len(slide.get_images())
            if count_image > 1:
                slide_text = slide.get_text()
                if slide_text.count('Рисунок') != count_image:
                    wrong_slide.append(num)
            elif len(slide.get_images()) == 1:
                # slide_text = slide.get_text()
                # slide_title = slide.get_titles()
                pass
        if wrong_slide:
            return answer(False, f'{wrong_slide}')
        else:
            return answer(True, 'Пройдена!')
