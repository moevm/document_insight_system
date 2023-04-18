from .style_info import StyleInfo


class ChapterObject:
    def __init__(self, object_type, data):
        self.type = object_type
        self.data = data

        self.style_info = StyleInfo(data.style)
        self.table = None


class ChapterObjectHeader(ChapterObject):
    def __init__(self, object_type, data):
        super().__init__(object_type, data)
        self.text = data.text


class ChapterObjectImage(ChapterObject):
    def __init__(self, object_type, data):
        super().__init__(object_type, data)


class ChapterObjectTable(ChapterObject):
    def __init__(self, object_type, table):
        super().__init__(object_type, table)
        self.data_matrix = [[c.paragraphs for c in row.cells] for row in table.rows]


class ChapterObjectList(ChapterObject):
    def __init__(self, object_type, data, list_of_paragraphs=None):
        super().__init__(object_type, data)
        self.data_list = list_of_paragraphs
