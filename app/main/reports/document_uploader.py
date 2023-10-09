from abc import ABC, abstractmethod

class DocumentUploader(ABC):

    @abstractmethod
    def upload(self):
        pass
    
    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def page_counter(self):
        pass

    # @abstractmethod
    # def make_chapters(self):
    #     pass

    # @abstractmethod
    # def make_headers(self):
    #     pass
