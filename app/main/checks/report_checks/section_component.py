from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportSectionComponent(BaseReportCriterion):
    label = "Проверка наличия необходимых компонентов указанного раздела и их форматирования"
    _description = "Проверка наличия необходимых компонентов раздела и форматирования (жирный шрифт)"
    id = 'report_section_component'

    def __init__(self, file_info, chapter='Введение', 
                 patterns=None,
                 bold_check_exceptions=None,
                 headers_map=None):
        super().__init__(file_info)
        self.intro = {}
        
        #больше компонент
        if patterns is None:
            patterns = [
                'актуальность',
                'объект исследования', 
                'предмет исследования',
                'цель работы',
                'задачи',
                'практическая значимость'
            ]
        
        #нет проверки на жирность 
        if bold_check_exceptions is None:
            bold_check_exceptions = ['актуальность']
        self.bold_check_exceptions = [txt.lower() for txt in bold_check_exceptions]
        
        if headers_map:
            self.config = headers_map
            self.chapter = ''
            patterns = ('цель', 'задач')
        else:
            self.chapter = chapter
            
        self.chapters = []
        self.patterns = []
        for pattern in patterns:
            self.patterns.append({
                "name": pattern.capitalize(),
                "text": pattern, 
                "marker": 0,
                "paragraph_index": None
            })

    def late_init(self):
        if not self.chapter:
            self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
            if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config, {}):
                self.chapter = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]["header_for_report_section_component"]
        self.chapters = self.file.make_chapters(self.file_type['report_type'])


    def _is_text_bold_in_paragraph(self, paragraph, search_text):
        '''конкретный текст выделен жирным в параграфе'''
        for run in paragraph.get('runs', []):
            run_text = run['text'].lower()
            if search_text.lower() in run_text:
                style = run.get('style')
                if style and hasattr(style, 'bold'):
                    if style.bold:
                        return True
        return False

    def _check_bold_formatting(self, pattern):
        '''название компоненты выделено жирным'''
        text_to_check = pattern['text'].lower()
        
        if text_to_check in self.bold_check_exceptions:
            return True
        
        if pattern['paragraph_index'] is None:
            return False
        
        if pattern['paragraph_index'] < len(self.file.styled_paragraphs):
            paragraph = self.file.styled_paragraphs[pattern['paragraph_index']]
            return self._is_text_bold_in_paragraph(paragraph, pattern['text'])
        
        return False

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        
        self.late_init()
        if not self.chapter:
            return answer(True, f'Данная проверка не предусмотрена для работы с темой "{self.headers_main}"')
        
        #выделяем введение
        self.intro = {}
        for intro in self.chapters:
            header = intro["text"].lower()
            if header.find(self.chapter.lower()) >= 0:
                self.intro = intro
                break

        if not self.intro:
            return answer(False, f'Раздел "{self.chapter}" не обнаружен!')

        #проверка наличия компонент
        for intro_par in self.intro["child"]:
            par = intro_par["text"].lower()
            for i in range(len(self.patterns)):
                if self.patterns[i]["marker"] == 0:  # ещё не найден
                    if par.find(self.patterns[i]["text"]) >= 0:
                        self.patterns[i]["marker"] = 1
                        self.patterns[i]["paragraph_index"] = intro_par["number"]
                        break

        missing_components = []
        bold_missing = []
        
        for pattern in self.patterns:
            if not pattern["marker"]:
                missing_components.append(pattern["name"])
            elif pattern["text"].lower() not in self.bold_check_exceptions:
                if not self._check_bold_formatting(pattern):
                    bold_missing.append(pattern["name"])

        errors = []
        if missing_components:
            missing_html = '<li>' + '</li><li>'.join(missing_components) + '</li>'
            errors.append(f'Не найдены следующие компоненты раздела "{self.chapter}": <ul>{missing_html}</ul>')
        
        if bold_missing:
            bold_html = '<li>' + '</li><li>'.join(bold_missing) + '</li>'
            errors.append(f'Следующие компоненты не выделены жирным шрифтом: <ul>{bold_html}</ul>')
        
        if errors:
            return answer(False, '<br>'.join(errors))
        else:
            return answer(True, f'Все необходимые компоненты раздела "{self.chapter}" обнаружены и правильно отформатированы!')
