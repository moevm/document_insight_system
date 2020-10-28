from app.parser.slide_basic import SlideBasic


def _is_title(node):
    for key in node.attributes:
        if (key[1] == "class") and (node.attributes[key] == "title"):
            return True
    return False


class SlideODP(SlideBasic):
    def __init__(self, container):
        SlideBasic.__init__(self, container)
        title = []
        texts = []

        for node in container.childNodes:
            if _is_title(node):
                self.__walk_children(node, title)
            else:
                node_text = []
                self.__walk_children(node, node_text)
                texts.append(node_text)

        self.title = "".join(title)
        for text in texts:
            self.text += " ".join(text) + "\n"  # For now text from multiple nodes is separated with new line.

    def __walk_children(self, child, child_container):
        if hasattr(child, "data"):
            child_container.append(child.data)
        else:
            for in_child in child.childNodes:
                self.__walk_children(in_child, child_container)
