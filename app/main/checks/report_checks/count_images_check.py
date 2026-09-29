from ..base_check import BaseReportCriterion, answer


class ReportCountImagesCheck(BaseReportCriterion):
    label = "Проверка на количество изображений"
    _description = 'Количество изображений (не включая "Приложение") должно быть не меньше минимального порога'
    id = "count_images_check"
    warning = True

    def __init__(self, file_info, min_cnt_img=8):
        super().__init__(file_info)
        self.min_cnt_img = min_cnt_img

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        
        #! self.file.page_count - возвращяет в большинстве случев ВСЕ страницы(включая Приложение). Проблема заключается, в том, что текущий regexp не обрабатывает все случаи.
        #! Необходимо уточнить есть ли уже ПР с исправлением
        img_counter = self.file.pdf_file.page_images_count(page_without_pril=self.file.page_count)

        if img_counter < self.min_cnt_img:
            result_str = f"Проверка не пройдена! В работе найдено {self.img_counter} изображений без учета приложения, минимальное количество - {self.min_cnt_img}"

            result_str += '''
                        Если в работе мало изображений, попробуйте сделать следующее:
                        <ul>
                            <li>Добавьте иллюстрации, поясняющие результаты работы (схемы, графики, скриншоты);</li>
                            <li>Перенесите самые значимые изображения из Приложения в основной текст работы;</li>
                            <li>Учтите, что считаются только страницы до раздела "Приложение";</li>
                            <li>если заголовок приложения оформлен неверно, его страницы посчитаются как основной текст.</li>
                        </ul>
                        '''
            return answer(False, result_str)
        else:
            return answer(True, 'Пройдена!')
