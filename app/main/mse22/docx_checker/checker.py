from zipfile import ZipFile
from xml.dom.minidom import parse


class Checker:
    def __init__(self, file, document=None):
        """
        Checker constructor
        
        Args:
            file: can be a path to a file (a string),
            a file-like object or a path-like object.
            
            document: python-docx.Document instance
        """
        self._file = file
        self._document = document
        
    def check_pages(self, lower_bound, upper_bound):       
        if self.pages_number < upper_bound and self.pages_number > lower_bound:
            return True
        return False
        
    @property
    def pages_number(self):
        """
        Property that returns number of pages in the 
        docx file by retrieving <Pages> N </Pages>
        from one of document's xml configuration files
        
        Returns:
            pages number (int) 
        """
        with ZipFile(self._file, "r") as z:
            xml_tree = parse(z.open("docProps/app.xml"))

        xml_tree.normalize()
        xml_pages = xml_tree.getElementsByTagName("Pages")[0]
        pages_count = xml_pages.childNodes[0].nodeValue

        return pages_count