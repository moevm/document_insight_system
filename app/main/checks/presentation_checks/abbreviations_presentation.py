import re
from ..base_check import BasePresCriterion, answer
from ..check_abbreviations import main_check, forming_response


class PresAbbreviationsCheck(BasePresCriterion):
    label = "Проверка расшифровки аббревиатур в презентации"
    description = "Все аббревиатуры должны быть расшифрованы при первом использовании"
    id = 'pres_abbreviations_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            slides_text = self.file.get_text_from_slides()
            title_page = slides_text[0]
            full_text = " ".join(slides_text)

            continue_check, res_str, unexplained_abbr = main_check(text=full_text, unverifiable_text=title_page)
            if not continue_check:
                return answer(True, res_str)
            
            
            unexplained_abbr_with_slides = {}

            for slide_num, slide_text in enumerate(slides_text, 0):
                for abbr in unexplained_abbr:
                    if abbr in slide_text and abbr not in unexplained_abbr_with_slides:
                        unexplained_abbr_with_slides[abbr] = slide_num
                        
            if not unexplained_abbr_with_slides:
                return answer(True, "Все аббревиатуры правильно расшифрованы")
            
            result_str = forming_response(unexplained_abbr_with_slides, lambda pages: self.format_page_link(pages))
            return answer(False, result_str)
                
        except Exception as e:
            return answer(False, f"Ошибка при проверке аббревиатур: {str(e)}")
