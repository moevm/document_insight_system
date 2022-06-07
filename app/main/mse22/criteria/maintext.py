from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

from app.main.mse22.document.page_object import PageObjectHeader

DEFAULT_STYLE = {
    'fields':{
        'font_name': ['Times New Roman'],
        'font_size': [12, 14],
        'bold': [False, None],
        'italic': [False, None],
        'alignment': [WD_ALIGN_PARAGRAPH.JUSTIFY],
        'first_line_indent': [Cm(1.25), None],
        'line_spacing': [Cm(1.5), None],
    },
    'name': 'Основной текст',
}

LISTING_STYLE = {
    'fields':{
        'font_name': ['Courier New'],
        'font_size': [11],
        'bold': [False, None],
        'italic': [False, None],
        'alignment': [WD_ALIGN_PARAGRAPH.JUSTIFY],
        'first_line_indent': [Cm(0), None],
        'line_spacing': [Cm(1), None],
    },
    'name': 'Листинг',
}


class MainText:
    def __init__(self, text_page_objects, styles=[DEFAULT_STYLE, LISTING_STYLE]):
        self.msg = ''
        self.output = True
        self.text_page_objects = [{'object': page_object, 'passed': None, 'error_sets': None}
                                         for page_object in text_page_objects
                                            if not getattr(page_object.style_info, 'bold', None)]
        self.styles = styles


    def check_text(self):

        # обновление значений, отвечающих за ошибки и результат проверки
        self.msg = ''
        self.output = True

        for object_dict in self.text_page_objects:
            object_dict['passed'] = None
            object_dict['error_sets'] = {style['name']: set() for style in self.styles}

        # итерация по каждому стилю
        for style in self.styles:
            for object_dict in self.text_page_objects:

                obj = object_dict['object']
                passed = object_dict['passed']
    
                if not passed:
                    if isinstance(obj, PageObjectHeader):
                        object_dict['passed'] = True

                        for style_field, available_values in style['fields'].items():
                            if getattr(obj.style_info, style_field, None) not in available_values:
                                object_dict['passed'] = False
                                object_dict['error_sets'][style['name']].add(style_field)
                                self.output = False

        
    def change_msg(self, msg):
        self.msg = msg
        
    def get_output(self):
        self.check_text()

        for page_object_dict in self.text_page_objects:
            obj = page_object_dict['object']

            if isinstance(obj, PageObjectHeader) and page_object_dict['passed'] == False:
                self.change_msg(self.msg + f'\n\nСтрока {obj.text}')

                for style in self.styles:
                    style_name = style['name']
                    self.change_msg(self.msg + f'\nСтиль {style_name}:')

                    for error_name in page_object_dict['error_sets'][style_name]:
                        if error_name == 'font_name':
                            error_info = '\nНеверный шрифт'
                            self.change_msg(self.msg + error_info)
                        
                        if error_name == 'font_size':
                            error_info = '\nНеверный размер шрифта'
                            self.change_msg(self.msg + error_info)
                        
                        if error_name == 'bold' or error_name =='italic':
                            error_info = '\nНеверный стиль шрифта'
                            self.change_msg(self.msg + error_info)
                        
                        if error_name == 'alignment':
                            error_info = '\nНеверное выравнивание'
                            self.change_msg(self.msg + error_info)
                        
                        if error_name == 'first_line_indent':
                            error_info = '\nНеверный отступ'
                            self.change_msg(self.msg + error_info)
                        
                        if error_name == 'line_spacing':
                            error_info = '\nНеверный межстрочный интервал'
                            self.change_msg(self.msg + error_info)
                
        if self.output:
            self.change_msg('Текст оформлен правильно')
            
        return self.output
    
