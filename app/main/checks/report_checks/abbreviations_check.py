from ..base_check import BaseReportCriterion, answer
from ..check_abbreviations import get_unexplained_abbrev

class AbbreviationsCheckPres(BaseReportCriterion):
    label = "Проверка расшифровки аббревиатур"
    description = "Все аббревиатуры должны быть расшифрованы при первом использовании"
    id = 'abbreviations_check'

    def __init__(self, file_info):
        super().__init__(file_info)


    def check(self):
        try:
            text = self._get_document_text()
            
            if not text:
                return answer(False, "Не удалось получить текст документа")
            
            abbr_is_finding, unexplained_abbr = get_unexplained_abbrev(text=text)
            
            if not abbr_is_finding:
                return answer(True, "Аббревиатуры не найдены в документе")
            
            if not unexplained_abbr:
                return answer(True, "Все аббревиатуры правильно расшифрованы")

            unexplained_abbr_with_page = {}
            
            for page_num in range(1, self.file.page_counter() + 1):
                text_on_page = self.file.pdf_file.text_on_page[page_num]

                for abbr in unexplained_abbr:
                    if abbr in text_on_page and abbr not in unexplained_abbr_with_page:
                        unexplained_abbr_with_page[abbr] = page_num


            result_str = "Найдены нерасшифрованные аббревиатуры при первом использовании:<br>"      
            page_links = self.format_page_link(list(unexplained_abbr_with_page.values()))
            for index_links, abbr in enumerate(unexplained_abbr_with_page):
                result_str += f"- {abbr} на странице {page_links[index_links]}<br>"
            result_str += "Каждая аббревиатура должна быть расшифрована при первом использовании в тексте.<br>"
            result_str += "Расшифровка должны быть по первыми буквам, например, МВД - Министерство внутренних дел.<br>"
            
            return answer(False, result_str)

        except Exception as e:
            return answer(False, f"Ошибка при проверке аббревиатур: {str(e)}")
                


    def _get_document_text(self):

        if hasattr(self.file, 'pdf_file'):
            page_texts = self.file.pdf_file.get_text_on_page()
            return " ".join(page_texts.values())
        elif hasattr(self.file, 'paragraphs'):
            text_parts = []
            for paragraph in self.file.paragraphs:
                text = paragraph.to_string()
                if '\n' in text:
                    text = text.split('\n')[1]
                text_parts.append(text)
            return "\n".join(text_parts)
        return None
