import re
from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer


class LitRefInChapter(BaseReportCriterion):
    label = "Проверка количества ссылок на источники в определенном разделе"
    description = ''
    id = 'references_in_chapter_check'

    def __init__(self, file_info, min_ref_value=0.5, max_ref_value=0.8, headers_map = None):
        super().__init__(file_info)
        self.chapters_for_lit_ref = {}
        self.lit_ref_count = {}
        self.min_ref_value = min_ref_value
        self.max_ref_value = max_ref_value
        if headers_map:
            self.config = headers_map
        else:
            self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])
        self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
        if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config):
            self.chapters_for_lit_ref = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['chapters_for_lit_ref']
        else:
            if 'any_header' in StyleCheckSettings.CONFIGS.get(self.config):
                self.chapters_for_lit_ref= StyleCheckSettings.CONFIGS.get(self.config)['any_header']['chapters_for_lit_ref']

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        if not self.chapters_for_lit_ref:
            return answer(True, 'Для загруженной работы данная проверка не предусмотрена')
        result = []
        result_str = f'Пройдена!'
        currant_head = ''
        chapter_for_check = 0
        for chapter in self.chapters:
            if chapter['style'] == "heading 2":
                header = chapter["text"].lower()
                if currant_head:
                    self.lit_ref_count[currant_head].append(chapter['number'])
                    if currant_head in self.chapters_for_lit_ref:
                        chapter_for_check += 1
                        ref_count = len(self.search_references(self.lit_ref_count[currant_head][0], self.lit_ref_count[currant_head][1]))
                        if ref_count > self.chapters_for_lit_ref[currant_head][1] or ref_count < self.chapters_for_lit_ref[currant_head][0]:
                            result.append(f'"{currant_head[0].upper() + currant_head[1:]}" : {ref_count}')
                self.lit_ref_count[header] = [chapter['number'],]
                currant_head = header
        if result:
            ref_value = round((chapter_for_check-len(result))/chapter_for_check, 2)
            result_str = (f'Доля соответствия количества ссылок необходимому в требуемых разделах равна {ref_value}'
                        f'<br>Количество ссылок на источники не удовлетворяет допустимому в следующих разделах: <br> {", ".join(res for res in result)}'
                        f'<br> Допустимые пороги количества ссылок: <br> {self.chapters_for_lit_ref}')
            if ref_value > self.max_ref_value:
                return answer(1, f'Пройдена! {result_str}')
            elif ref_value > self.min_ref_value:
                return answer(ref_value, f'Частично пройдена! {result_str}')
            else:
                return answer(0, f'Не пройдена! {result_str}')
        else:
            return answer(1, result_str)
        
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
