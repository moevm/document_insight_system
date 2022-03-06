from odf import opendocument, draw

from app.utils import tict


class OdfDocument:
    def __init__(self, filename):
        self._document = opendocument.load(filename)
        self._pages = self._document.getElementsByType(draw.Page)
        self._auto_styles = {}
        for style in self._document.automaticstyles.childNodes:
            style_name = tict.get(style.attributes, "name")
            style_params = {}
            for child in style.childNodes:
                style_params.update(tict.dictify(child.attributes))
            self._auto_styles[style_name] = style_params
