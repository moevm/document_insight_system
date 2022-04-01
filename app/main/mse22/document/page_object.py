class PageObjectHeader:
    pass


class PageObjectImage:
    pass


class PageObjectTable:
    pass


class PageObjectData:
    pass


class PageObjectTypes:
    pass


class PageObject(PageObjectHeader, PageObjectImage, PageObjectTable, PageObjectData):
    def __init__(self, type, data):
        self.type = type
        self.data = data
