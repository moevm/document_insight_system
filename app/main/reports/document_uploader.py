from abc import ABC, abstractmethod

class DocumentUploader(ABC):

    def __init__(self):
        self.chapters = []
        self.paragraphs = []
        self.tables = []
        self.styled_paragraphs = []
        self.pdf_file = None
        self.literature_header = []
        self.literature_page = 0
        self.first_lines = []
        self.page_count = 0

    @abstractmethod
    def upload(self):
        pass
    
    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def parse_effective_styles(self):
        pass

    @abstractmethod
    def page_counter(self):
        pass

    @abstractmethod
    def make_chapters(self, work_type):
        pass

    @abstractmethod
    def find_header_page(self, work_type):
        pass

    @abstractmethod
    def find_literature_vkr(self, work_type):
        pass

    @abstractmethod
    def find_literature_page(self, work_type):
        pass
    
    @abstractmethod
    def show_chapters(self, work_type):
        pass
