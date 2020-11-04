from app.parser.odp.presentation_odp import PresentationODP
from app.parser.pptx.presentation_pptx import PresentationPPTX
import re
import os


class Parser:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.presentation = None
        self.state = 0
        self.text = []
        self.titles = []
        self.parse_presentation()

    def get_presentation_name(self):
        return self.presentation_name

    def parse_presentation(self):
        if str(self.presentation_name).endswith('.ppt') or str(self.presentation_name).endswith('.pptx'):
            try:
                self.state = 1
                self.presentation = PresentationPPTX(self.presentation_name)
                self.state = 2
                self.text = self.presentation.get_text_from_slides()
                self.titles = self.presentation.get_titles()
                self.state = 3
            except Exception as err:
                print(err)
                self.state = -1
        elif str(self.presentation_name).endswith('.odp'):
            try:
                self.state = 1
                self.presentation = PresentationODP(self.presentation_name)
                self.state = 2
                self.text = self.presentation.get_text_from_slides()
                self.titles = self.presentation.get_titles()
                self.state = 3
            except Exception as err:
                print(err)
                self.state = -1

    def get_titles(self):
        return self.titles

    def get_text(self):
        return self.text

    def get_state(self):
        return self.state

    def check_title_size(self, filename, upload_folder):
        i = 0
        error_slides = ''
        for title in self.titles:
            i += 1
            title = str(title).replace('\x0b', '\n')
            if '\n' in title or '\r' in title:
                titles = []
                for t in re.split('\r|\n', title):
                    if t != '':
                        titles.append(t)
                if len(titles) > 2:
                    error_slides += str(i) + ' '
        try:
            with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_error_with_title_size.txt', 'w') as answer:
                answer.write(error_slides)
        except Exception as err:
            print(err)
            print("Что-то пошло не так")
        return error_slides

    def find_definite_slide(self, type_of_slide):
        i = 0
        for title in self.titles:
            i += 1
            if str(title).lower().find(str(type_of_slide).lower()) != -1:
                return i

    def check_slides_enumeration(self):
        error = ""
        if self.presentation.slides[0].page_number[0] != -1:
            error += "0 "
        for i in range(1, len(self.presentation.slides)):
            if self.presentation.slides[i].page_number[0] != i + 1:
                error += str(i) + " "
        return error
