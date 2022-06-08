import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm

from app.main.mse22.document.document import Document
from app.main.mse22.checks.font_report_check import FontReportCheck
from app.main.mse22.checks.banned_words_report_check import BannedWordsReportCheck


class BaseCriterion:
    def __init__(self, document, form_data):
        self.succeeded = True
        self.message = ""
        self.checks = []
        self.document = document
        if form_data["fonts"] is not None:
            criteria = []
            main_text_criteria = {"name": "Основной текст", "fields": {}}
            self.fill_formatting_criteria(form_data["fonts"]["main"], main_text_criteria["fields"])
            for key in main_text_criteria["fields"]:
                main_text_criteria["fields"][key].append(None)
            criteria.append(main_text_criteria)
            if form_data["fonts"]["listing"]["allow_listings"]:
                listing_criteria = {"name": "Листинг", "fields": {}}
                self.fill_formatting_criteria(form_data["fonts"]["listing"], listing_criteria["fields"])
                for key in listing_criteria["fields"]:
                    listing_criteria["fields"][key].append(None)
                criteria.append(listing_criteria)
            self.checks.append(FontReportCheck(criteria))
        if form_data["banned_words"] is not None:
            self.checks.append(BannedWordsReportCheck(form_data["banned_words"]))

    def check(self):
        for check in self.checks:
            result = check.check(self.document.pages)
            self.message += result["message"]
            self.succeeded &= result["succeeded"]

    @staticmethod
    def fill_formatting_criteria(main_font_props, main_font_values):
        for key in main_font_props:
            if main_font_props[key] is None:
                continue
            if key in ["first_line_indent", "line_spacing"]:
                main_font_values[key] = [round(Cm(length) / 1000) * 1000 for length in main_font_props[key]]
            elif key in ["bold", "italic"]:
                if main_font_props[key]:
                    main_font_values[key] = [False, True]
                else:
                    main_font_props[key] = [False]
            elif key == "alignment":
                if main_font_props[key] == "Left":
                    main_font_values[key] = [WD_ALIGN_PARAGRAPH.LEFT]
                elif main_font_props[key] == "Center":
                    main_font_values[key] = [WD_ALIGN_PARAGRAPH.CENTER]
                elif main_font_props[key] == "Justify":
                    main_font_values[key] = [WD_ALIGN_PARAGRAPH.JUSTIFY]
                elif main_font_props[key] == "Right":
                    main_font_values[key] = [WD_ALIGN_PARAGRAPH.RIGHT]
            # elif key == "line_spacing":
            #    main_font_values[key] = []
            #    for spacing_type in main_font_props[key]:
            #        if spacing_type == 1:
            #            main_font_values[key].append(WD_LINE_SPACING.SINGLE)
            #        elif spacing_type == 1.5:
            #            main_font_values[key].append(WD_LINE_SPACING.ONE_POINT_FIVE)
            #        elif spacing_type == 2:
            #            main_font_values[key].append(WD_LINE_SPACING.DOUBLE)
            elif key == "allow_listings":
                continue
            else:
                main_font_values[key] = main_font_props[key]


# Tests
form_data_empty = {
    "fonts": None,
    "banned_words": None
}

form_data_1 = {
    "fonts": {
        "main": {
            "font_size": [14],
            "font_name": ["Times New Roman"],
            "bold": False,
            "italic": False,
            "alignment": "Justify",
            "first_line_indent": [1.25],
            "line_spacing": [1.5]
        },
        "listing": {
            "allow_listings": True,
            "font_size": [10, 11, 12],
            "font_name": ["Courier New"],
            "bold": False,
            "italic": False,
            "alignment": "Justify",
            "first_line_indent": [0],
            "line_spacing": [1]
        }
    },
    "banned_words": ["wikipedia", "википедия"]
}

form_data_2 = {
    "fonts": {
        "main": {
            "font_size": [14],
            "font_name": ["Times New Roman"],
            "bold": True,
            "italic": True,
            "alignment": "Justify",
            "first_line_indent": None,
            "line_spacing": None
        },
        "listing": {
            "allow_listings": False
        }
    },
    "banned_words": None
}

if __name__ == "__main__":
    filename = "../for_testing/test_files/docx/passing-1.docx"
    docx_document = docx.Document(filename)
    document = Document(docx_document, filename, "LR")
    criterion = BaseCriterion(document, form_data_1)
    criterion.check()
    print(criterion.succeeded, "\n")
    print(criterion.message)
