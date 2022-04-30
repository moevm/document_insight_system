from .style_info import StyleInfo


class PageObject:
    def __init__(self, object_type, data):
        self.type = object_type
        self.data = data

        self.style_info = StyleInfo(data.style)
        self.image = None
        self.table = None


class PageObjectHeader(PageObject):
    def __init__(self, object_type, data):
        super().__init__(object_type, data)
        self.text = data.text


class PageObjectImage(PageObject):
    def __init__(self, object_type, data, image=None):
        super().__init__(object_type, data)
        self.image = image


class PageObjectTable(PageObject):
    def __init__(self, object_type, table):
        super().__init__(object_type, table)
        self.data_matrix = [[c.text for c in row.cells] for row in table.rows]


class PageObjectList(PageObject):
    def __init__(self, object_type, data, list_of_paragraphs=None):
        super().__init__(object_type, data)
        self.data_list = list_of_paragraphs
