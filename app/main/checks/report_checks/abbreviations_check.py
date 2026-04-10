from ..base_check import BaseReportCriterion, answer
from ..check_abbreviations import main_check, forming_response


class ReportAbbreviationsCheck(BaseReportCriterion):
    label = "Проверка расшифровки аббревиатур"
    id = 'report_abbreviations_check'

    def __init__(self, file_info):
        super().__init__(file_info)


    def check(self):
        try:
            text = self._get_document_text()
            
            headings=['СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ', 'ПРИЛОЖЕНИЕ', 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ']
            unverifiable_text = self._get_unverifiable_text(headings)


            continue_check, res_str, unexplained_abbr = main_check(text=text, unverifiable_text=unverifiable_text)
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
            # return answer(True, f"self.file.make_chapters(self.file_type['report_type']):\n {self.file.make_chapters(self.file_type['report_type'])}")

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
    
    def _get_text_into_sections(self, headings):
        chapters = self.file.make_chapters(self.file_type['report_type'])
        text_parts = []
        
        for chapter in chapters:
            chapter_title = chapter.get('text', '').upper()
            
            if any(stop.upper() in chapter_title for stop in headings):

                text_parts.append(chapter['text'])
                
                def add_child_text(child_elements):
                    for child in child_elements:
                        if child.get('text'):
                            text_parts.append(child['text'])
                        if child.get('child'):
                            add_child_text(child['child'])
                
                if chapter.get('child'):
                    add_child_text(chapter['child'])
        
        return " ".join(text_parts)

    def _get_text_title_page(self):
        title_page = self.file.pdf_file.text_on_page[1]
        return title_page
    
    def _get_unverifiable_text(self, unverifiable_headings):
        unverifiable_text = self._get_text_title_page() + self._get_text_into_sections(unverifiable_headings)
        return unverifiable_text