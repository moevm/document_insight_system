from app.parser.slide_basic import SlideBasic


def _is_title(node):
    for key in node.attributes:
        if (key[1] == "class") and (node.attributes[key] == "title"):
            return True
    return False


def _is_notes(node):
    return node.tagName == "presentation:notes"


def _contains_page_number(node):
    for key in node.attributes:
        if key[1] == "page-number":
            return True
    return False


class SlideODP(SlideBasic):
    def __init__(self, container):
        SlideBasic.__init__(self, container)
        title = []
        texts = []

        self.page_number = [-1.0, -1.0, -1]

        for node in container.childNodes:
            if _is_title(node):
                self.__walk_children(node, title)
            elif _is_notes(node):
                for child in node.childNodes:
                    if _contains_page_number(child):
                        for key in child.attributes:
                            if key[1] == "page-number":
                                self.page_number[2] = int(child.attributes[key])
                            elif key[1] == "x":
                                self.page_number[0] = float(child.attributes[key][:-3])
                            elif key[1] == "y":
                                self.page_number[1] = float(child.attributes[key][:-3])
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
