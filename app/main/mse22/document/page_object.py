from .style_info import StyleInfo

class PageObject:
    def __init__(self, object_type, data):
        self.type = object_type
        self.data = data
        
        self.style_info = StyleInfo(data.style)
        self.image = None
        self.table = None
        
  
class PageObjectHeader(PageObject):
    def __init__(self, data):
        super().__init__(data)
        self.text = data.text


class PageObjectImage(PageObject):
    def __init__(self, data, image):
        super().__init__(data)
        self.image = image


class PageObjectTable(PageObject):
    def __init__(self, data, table):
        super().__init__(data)
        self.data_matrix = [[c.text for c in row.cells] for row in table.rows]


class PageObjectList(PageObject):
    def __init__(self, data, list_of_paragraphs):
        super().__init__(data)
        self.data_list = list_of_paragraphs
   