import re
from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer


class LitRefInChapter(BaseReportCriterion):
    label = "Проверка количества ссылок на источники в определенном разделе"
    description = ''
    id = 'references_in_chapter_check'

    def __init__(self, file_info, chapters_for_lit_ref = {
        # 'введение', "определения, обозначения и сокращения", "заключение"
        }, min_ref = 1, headers_map = None):
        super().__init__(file_info)
        self.lit_ref_count = {}
        self.min_ref = min_ref
        if headers_map:
            self.chapters_for_lit_ref = StyleCheckSettings.CONFIGS.get(headers_map)[0]["headers_for_lit_count"]
        else:
            self.chapters_for_lit_ref = chapters_for_lit_ref

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = []
        result_str = f'Пройдена!'
        self.late_init()
        currant_head = ''
        for chapter in self.chapters:
            if chapter['style'] == "heading 2":
                header = chapter["text"].lower()
                if currant_head:
                    self.lit_ref_count[currant_head].append(chapter['number'])
                    if currant_head in self.chapters_for_lit_ref:
                        ref_count = len(self.search_references(self.lit_ref_count[currant_head][0], self.lit_ref_count[currant_head][1]))
                        if ref_count > self.min_ref:
                            result.append(f'"{currant_head[0].upper() + currant_head[1:]}" : {ref_count}')
                self.lit_ref_count[header] = [chapter['number'],]
                currant_head = header
        if result:
            result_str = f'Количество ссылок на источники превышает допустимое ({self.min_ref}) в следующих разделах: <br> {", ".join(res for res in result)}'
            return answer(False, result_str)
        else:
            return answer(True, result_str)
        
    def search_references(self, start_par, end_par):
        array_of_references = []
        for i in range(start_par, end_par):
            if isinstance(self.file.paragraphs[i], str):
                detected_references = re.findall(r'\[[\d \-,]+\]', self.file.paragraphs[i])
            else:
                detected_references = re.findall(r'\[[\d \-,]+\]', self.file.paragraphs[i].paragraph_text)
            if detected_references:
                for reference in detected_references:
                    for one_part in re.split(r'[\[\],]', reference):
                        if re.match(r'\d+[ \-]+\d+', one_part):
                            start, end = re.split(r'[ -]+', one_part)
                            for k in range(int(start), int(end) + 1):
                                array_of_references.append((k))
                        elif one_part != '':
                            array_of_references.append(int(one_part))
        return array_of_references
