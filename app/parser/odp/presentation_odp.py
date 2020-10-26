import zipfile
import xml.parsers.expat
from app.parser.odp.tree_builder import TreeBuilder
from app.parser.odp.element import Element

class PresentationODP:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.slides = []
        self.text = ""
        self.titles = []
        self.treebuilder = None

    def initialization(self):
        ziparchive = zipfile.ZipFile(self.presentation_name, "r")
        xmldata = ziparchive.read("content.xml")
        ziparchive.close()

        parser = xml.parsers.expat.ParserCreate()
        self.treebuilder = TreeBuilder()

        parser.StartElementHandler = self.treebuilder.start_element
        parser.EndElementHandler = self.treebuilder.end_element
        parser.CharacterDataHandler = self.treebuilder.char_data
        parser.Parse(xmldata, True)

    def showtree(self, node):
        # print(prefix, node.name)
        for e in node:
            if isinstance(e, Element):
                self.showtree(e)
            else:
                self.text += e + '\n'

    def get_text_from_slides(self):
        self.initialization()
        self.showtree(self.treebuilder.root)
        return self.text