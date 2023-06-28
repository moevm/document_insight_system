import re

from ..base_check import BaseReportCriterion, answer


class ImageReferences(BaseReportCriterion):
    description = "Проверка наличия ссылок на все рисунки"
    id = 'image_references'

    def __init__(self, file_info, image_style="ВКР_Подпись для рисунков"):
        super().__init__(file_info)
        self.headers = []
        self.last_child_number = 0
        self.image_style = image_style

    def late_init_vkr(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result_str = ''
        if self.file_type['report_type'] == 'VKR':
            self.late_init_vkr()
            if not len(self.headers):
                return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
            number_of_images, all_numbers = self.count_images_vkr()
            if not number_of_images:
                return answer(False, f'Не найдено ни одного рисунка.<br><br>Убедитесь, что для подписи рисунка был '
                                     f'использован стиль {self.image_style}, а рисунок подписан '
                                     f'"Рисунок <Номер рисунка> -- <Название рисунка>".')
        else:
            return answer(False, 'Во время обработки произошла критическая ошибка')
        references = self.search_references()
        if len(references.symmetric_difference(all_numbers)) == 0:
            return answer(True, f"Пройдена!")
        elif len(references.difference(all_numbers)):
            if len(all_numbers.difference(references)) == 0:
                references -= all_numbers
                result_str += f'Упомянуты несуществующие рисунки: {", ".join(str(num) for num in sorted(references))} ' \
                              f'<br> Номера рисунков: {", ".join(num for num in sorted(all_numbers))}<br><br>'
            else:
                extras = references - all_numbers
                unnamed = all_numbers - references
                result_str += f'Упомянуты несуществующие рисунки: {", ".join(str(num) for num in sorted(extras))} ' \
                              f'<br> А также упомянуты не все рисунки: {", ".join(str(num) for num in sorted(unnamed))} ' \
                              f'<br> Номера рисунков: {", ".join(num for num in sorted(all_numbers))}<br><br>'
        else:
            all_numbers -= references
            result_str = f'Упомянуты не все рисунки.<br>Список рисунков без упоминания: ' \
                         f'{", ".join(str(num) for num in sorted(all_numbers))} <br> Номера рисунков: ' \
                         f'{", ".join(num for num in sorted(all_numbers))}<br><br>'
        result_str += f'''
                    Если возникли проблемы, попробуйте сделать следующее:
                    <ul>
                        <li>Убедитесь, что для подписи рисунка используется шаблон "Рисунок <Номер рисунка> -- <Название рисунка>";</li>
                        <li>Убедитесь, что для ссылки на рисунок используется шаблон "рис. <Номер рисунка>";</li>
                        <li>Убедитесь, что для оформления подписи рисунка был использован стиль "{self.image_style}";</li>
                    </ul>
                    '''
        return answer(False, result_str)

    def search_references(self):
        array_of_references = set()
        for i in range(0, self.last_child_number):
            detected_references = re.findall(r'[Рр]ис\. [\d .,]+', self.file.paragraphs[i].paragraph_text)
            if detected_references:
                for reference in detected_references:
                    for one_part in re.split(r'[Рр]ис\.|,| ', reference):
                        if re.match(r'\d+(\.\d+)*\.$', one_part):
                            number = one_part[:-1]
                            array_of_references.add(number)
                        elif re.match(r'\d+(\.\d+)*', one_part):
                            array_of_references.add(one_part)
        return array_of_references

    def count_images_vkr(self):
        images_counter = 0
        child_number = 0
        all_numbers = set()
        for header in self.headers:
            for child in header["child"]:
                child_number = child["number"]
                if child["style"] == self.image_style.lower():
                    child_text = child["text"].strip()
                    if re.search(r'Рисунок [.\d]+', child_text):
                        number_seq = child_text.split('Рисунок')[1]
                        for number in re.split(r' ', number_seq):
                            if number:
                                if number.find("-") >= 0:
                                    break
                                if re.search(r'\d+(\.\d+)*', number):
                                    images_counter += 1
                                    all_numbers.add(number)
                                    break
        self.last_child_number = child_number
        return images_counter, all_numbers
