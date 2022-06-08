from app.main.mse22.document.page_object import PageObjectTable
from docx.enum.text import WD_ALIGN_PARAGRAPH

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

            if hasattr(obj.style_info, 'alignment') and obj.style_info.alignment != alignment:
                if obj.style_info.alignment != None:
                    errors.add('Неверное выравнивание')
            
            if hasattr(obj.style_info, 'font_name') and obj.style_info.font_name != font:
                if obj.style_info.font_name != None:
                    errors.add('Неверное шрифт')
            
            if hasattr(obj.style_info, 'font_size') and obj.style_info.font_size != size:
                if obj.style_info.font_size != None:
                    errors.add('Неверное шрифт')

            if errors:
                passed = False
                msg += f'\n\nТаблица {index + 1}'
                for err in errors:
                    msg += f'\n {err}'
                 
        if passed:
            msg = 'Таблицы оформлены верно\n'
        
        return msg
        

        


            
            
    
