import re
from ..base_check import BasePresCriterion, answer
from ..check_abbreviations import get_unexplained_abbrev


class PresAbbreviationsCheck(BasePresCriterion):
    label = "Проверка расшифровки аббревиатур в презентации"
    description = "Все аббревиатуры должны быть расшифрованы при первом использовании"
    id = 'pres_abbreviations_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            slides_text = self.file.get_text_from_slides()
            
            if not slides_text:
                return answer(False, "Не удалось получить текст презентации")

            full_text = " ".join(slides_text)

            abbr_is_finding, unexplained_abbr = get_unexplained_abbrev(text=full_text)
            
    
            unexplained_abbr_with_slides = {}

            for slide_num, slide_text in enumerate(slides_text, 1):
                for abbr in unexplained_abbr:
                    if abbr in slide_text and abbr not in unexplained_abbr_with_slides:
                        unexplained_abbr_with_slides[abbr] = slide_num

            result_str = "Найдены нерасшифрованные аббревиатуры при первом использовании:<br>"
            slide_links = self.format_page_link(list(unexplained_abbr_with_slides.values()))
            for index_links, abbr in enumerate(unexplained_abbr_with_slides):
                result_str += f"- {abbr} на слайде {slide_links[index_links]}<br>"
            
            result_str += "<br>Каждая аббревиатура должна быть расшифрована при первом использовании в презентации.<br>"
            result_str += "Расшифровка должны быть по первыми буквам, например, МВД - Министерство внутренних дел.<br>"

            return answer(False, result_str)
                
        except Exception as e:
            return answer(False, f"Ошибка при проверке аббревиатур: {str(e)}")
    