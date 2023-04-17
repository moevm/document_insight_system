from app.utils import tict
from ..slide_basic import SlideBasic


def _is_title(node):
    return tict.get(node.attributes, "class") == "title"


def _is_notes(node):
    return node.tagName == "presentations:notes"


def _page_number_valid(node, slide, styles):
    style = tict.get(slide.attributes, "style-name")
    if "display-page-number" in styles[style]:
        display_page_number = styles[style]["display-page-number"] == "true"
    else:
        display_page_number = False

    return (tict.has(node.attributes, "page-number")) and display_page_number


class SlideODP(SlideBasic):
    def __init__(self, container, styles):
        SlideBasic.__init__(self, container)
        title = []
        texts = []

        self.page_number = [-1.0, -1.0, -1]

        for node in container.childNodes:
            if _is_title(node):
                self.__walk_children(node, title)
            elif _is_notes(node):
                for child in node.childNodes:
                    if _page_number_valid(child, container, styles):
                        self.page_number[0] = int(tict.get(child.attributes, "page-number"))
                        self.page_number[1] = float(tict.get(child.attributes, "x")[:-2])
                        self.page_number[2] = float(tict.get(child.attributes, "y")[:-2])
            else:
                node_text = []
                self.__walk_children(node, node_text)
                texts.append(node_text)

        self.title = "\n".join(title)
        for text in texts:
            self.text += " ".join(text) + "\n"  # For now text from multiple nodes is separated with new line.

    def __walk_children(self, child, child_container):
        if hasattr(child, "data"):
            child_container.append(child.data)
        else:
            for in_child in child.childNodes:
                self.__walk_children(in_child, child_container)

    def __str__(self):
        return super().__str__()
