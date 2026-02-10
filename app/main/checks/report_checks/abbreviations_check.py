from ..base_check import BaseReportCriterion, answer
from ..check_abbreviations import main_check, forming_response


class ReportAbbreviationsCheck(BaseReportCriterion):
    label = "Проверка расшифровки аббревиатур"
    description = "Все аббревиатуры должны быть расшифрованы при первом использовании"
    id = 'report_abbreviations_check'

    def __init__(self, file_info):
        super().__init__(file_info)


    def check(self):
        try:
            text = self._get_document_text()
            title_page = self.file.pdf_file.text_on_page[1]

            continue_check, res_str, unexplained_abbr = main_check(text=text, title_page=title_page)
            if not continue_check:
                return answer(True, res_str)
            
            unexplained_abbr_with_page = {}
            
            for page_num in range(1, self.file.page_counter() + 1):
                text_on_page = self.file.pdf_file.text_on_page[page_num]

                for abbr in unexplained_abbr:
                    if abbr in text_on_page and abbr not in unexplained_abbr_with_page:
                        unexplained_abbr_with_page[abbr] = page_num
                
            if not unexplained_abbr_with_page:
                return answer(True, "Все аббревиатуры правильно расшифрованы")
            result_str = forming_response(unexplained_abbr_with_page, lambda pages: self.format_page_link(pages))
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
    