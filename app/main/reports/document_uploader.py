from abc import ABC, abstractmethod

class DocumentUploader(ABC):

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
