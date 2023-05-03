from ..base_check import BasePresCriterion, answer


class PresImageShareCheck(BasePresCriterion):
    description = "Проверка доли объема презентации, приходящейся на изображения"
    id = 'pres_image_share'

    def __init__(self, file_info, limit=0.9):
        super().__init__(file_info)
        self.limit = limit

    def check(self):
        buf = []
        count = 0
        for slide in self.file.slides:
            if len(slide.get_images()) > 0:
                count += 1
                buf.append(slide.get_page_number())
        buf =  ' '.join(list(map(str,buf)))
        if count / len(self.file.slides) > self.limit:
            return answer(False, f'Проверка не пройдена! Изображения в презентации занимают около {round(count / len(self.file.slides), 2)} количества всех слайдов, \
                                        ограничение - {round(self.limit, 2)}')
        else:
            return answer(True, f'Пройдена!')
        return answer(False, 'Во время обработки произошла критическая ошибка')
