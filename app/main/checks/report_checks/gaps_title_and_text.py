from ..base_check import BaseReportCriterion, answer


class ReportGapsBetweenTitleAndTextCheck(BaseReportCriterion):
    label = "Проверка разрывов между заголовком и текстом"
    _description = "Не должно быть разрывов между заголовком и текстом. Когда заголовок на одной странице, а текст уже на другой."
    id = 'report_gaps_between_title_and_text_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            headers = self.file.make_chapters(self.file_type['report_type'])
            if not headers:
                return answer(False, "Не найдено ни одного заголовка.")

            list_page_num = []
            for header in headers:
                if "heading" in header['style']:
                    page_num, perfom = self.search(header["text"], self.get_text_after_title(header))
                    if not perfom and page_num not in list_page_num:
                        list_page_num.append(page_num)

            if list(list_page_num) == 0:
                return answer(True, "Проверка разрывов между заголовком и текстом пройдена!")
            
            return answer(False, f"Проверка разрывов между заголовком и текстом не пройдена! Страницы, на которых найдено несоответствие: {'\n'.join(list_page_num)}")

        except Exception as e:
            return answer(False, f"Ошибка про проверке разрывов между заголовком и текстом: {str(e)}")

    def search(self, str_1, str_2):
        for page_num in range(1, self.file.page_counter() + 1):
            text_on_page = self.file.pdf_file.text_on_page[page_num]

            if str_1 in text_on_page and str_2 in text_on_page:
                return page_num, True
            
            if str_1 not in text_on_page and str_2 not in text_on_page:
                continue

            return page_num, False

    
    def get_text_after_title(self, header, chars_count=40):

        if 'child' not in header or not header['child']:
            return ""
        
        full_text = ""
        for child in header['child']:
            if child.get('text'):
                full_text += child['text'] + " "
                if len(full_text) >= chars_count:
                    break
        
        return full_text[:chars_count].strip()
