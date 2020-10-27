import zipfile
import xml.parsers.expat
from app.parser.odp.tree_builder import TreeBuilder
from app.parser.odp.element import Element
from app.parser.presentation_basic import PresentationBasic


class PresentationODP(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name, [], "", [])
        self.treebuilder = None
        self.initialization()

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

    def showtree(self, node, true_if_text_false_if_titles):
        # print(prefix, node.name)
        for e in node:
            if isinstance(e, Element):
                self.showtree(e, true_if_text_false_if_titles)
            else:
                if true_if_text_false_if_titles:
                    self.text += e + '\n'
                else:
                    self.titles.append(e)

    def showtree_splitted(self, node, true_if_text_false_if_titles):
        for e in node:
            if isinstance(e, Element):
                if true_if_text_false_if_titles:
                    if "presentation:class" in e.attrs and e.attrs["presentation:class"] != "title":
                        self.showtree(e, true_if_text_false_if_titles)
                    else:
                        self.showtree_splitted(e, true_if_text_false_if_titles)
                else:
                    if "presentation:class" in e.attrs and e.attrs["presentation:class"] == "title":
                        self.showtree(e, true_if_text_false_if_titles)
                    else:
                        self.showtree_splitted(e, true_if_text_false_if_titles)

    def get_text_from_slides(self):
        self.showtree_splitted(self.treebuilder.root, True)
        return self.text

    def get_titles(self):
        self.showtree_splitted(self.treebuilder.root, False)
        return self.titles

