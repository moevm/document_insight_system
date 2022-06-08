from app.main.mse22.document.page_object import PageObjectTable
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.main.mse22.document.style_info import StyleInfo

# class FQWCritertion(BaseCriteterion):
class FQWCriterion():
    def __init__(self, title=None, subtitle=None, *args, **kwargs):
        # super().__init__(*args, **kwargs)
        self.title = title
        self.subtitle = subtitle

    def fqw_tables(
            self,          
            page_objects, 
            alignment=WD_ALIGN_PARAGRAPH.LEFT, 
            font='Times New Roman', 
            size=14
    ):
        table_objects = [{'obj': obj, 'errors': set()} for obj in page_objects if isinstance(obj, PageObjectTable)]
        passed = True
        msg = ''

        for index, object_dict in enumerate(table_objects):
            obj = object_dict['obj']
            errors = object_dict['errors']
 
            if len(obj.data_matrix) > 5:
                size = 12
            
            # проверка оформления
            for row in obj.data_matrix:
                for cell in row:
                    for paragraph in cell:
                        p_style = StyleInfo(paragraph.style)

                        if hasattr(p_style, 'alignment') and p_style.alignment != alignment:
                            if p_style.alignment != None:
                                errors.add('Неверное выравнивание')
                        
                        if hasattr(p_style, 'font_name') and p_style.font_name != font:
                            if p_style.font_name != None:
                                errors.add('Неверный шрифт')
                        
                        if hasattr(p_style, 'font_size') and p_style.font_size != size:
                            if p_style.font_size != None:
                                errors.add('Неверный размер шрифта')

            if errors:
                passed = False
                msg += f'\n\nТаблица {index + 1}'
                for err in errors:
                    msg += f'\n {err}'
                 
        if passed:
            msg = 'Таблицы оформлены верно\n'
        
        return msg
        

        


            
            
    
