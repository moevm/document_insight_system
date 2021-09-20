from flask import url_for

def answer(mod, value, *args):
    return {
        'pass': bool(mod),
        'value': value,
        'verdict': (args)
    }

class BaseCheck:
    def __init__(self, presentation):
        self.presentation = presentation

    def check(self):
        raise NotImplementedError()

    def format_page_link(self, error):
        base_pdf_link = url_for('get_pdf', _id=self.pdf_id)
        res = []
        for err in error:
            page = base_pdf_link + "#page=" + str(err)
            res.append('<a href='+ '"' + page + '"'+ 'target="_blank" rel="noopener">' + str(err) + '<a>')
        return res
