from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm
from collections import defaultdict

DEFAULT_TEXT_CRITERIA = {
    'font_name': ['Times New Roman'],
    'font_size': [14],
    'bold': [False, None],
    'italic': [False, None],
    'alignment': [WD_ALIGN_PARAGRAPH.JUSTIFY],
    'first_line_indent': [Cm(1.25), None],
    'line_spacing': [Cm(1.5), None],
}

class MainText:
    def __init__(self, text_page_objects, criteria=DEFAULT_TEXT_CRITERIA):
        self.msg = ''
        self.output = True
        self.text_page_objects = text_page_objects
        self.criteria = criteria
        self._errors = defaultdict(list)
        
    def check_text(self):
        self._errors.clear()
        self.msg = ''
        self.output = True
        for obj in self.text_page_objects:
            for k, v in self.criteria.items():
                if getattr(obj.style_info, k, None) not in v:
                    self._errors[k] += [obj.text]
                    self.output = False
            
        
    def change_msg(self, msg):
        self.msg = msg
        
    def get_output(self):
        for error_name, strings in self._errors.items():
            if error_name == 'font_name':
                error_info = '\nНеверный шрифт в строках:\n' + '\n'.join(strings) 
                self.change_msg(self.msg + error_info)
            
            if error_name == 'font_size':
                error_info = '\nНеверный размер шрифта в строках:\n' + '\n'.join(strings) 
                self.change_msg(self.msg + error_info)
            
            if error_name == 'bold' or error_name =='italic':
                error_info = '\nНеверный стиль шрифта в строках:\n' + '\n'.join(strings) 
                self.change_msg(self.msg + error_info)
            
            if error_name == 'alignment':
                error_info = '\nНеверное выравнивание в строках:\n' + '\n'.join(strings) 
                self.change_msg(self.msg + error_info)
            
            if error_name == 'first_line_indent':
                error_info = '\nНеверный отступ в строках:\n' + '\n'.join(strings) 
                self.change_msg(self.msg + error_info)
            
            if error_name == 'line_spacing':
                error_info = '\nНеверный межстрочный интервал в строках:\n' + '\n'.join(strings) 
                self.change_msg(self.msg + error_info)
                
        if not self.msg:
            self.msg = 'Текст оформлен правильно'
            
        return self.output
    
