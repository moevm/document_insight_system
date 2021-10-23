from flask import url_for

def answer(mod, *args):
    return {
        'pass': bool(mod),
        'verdict': (args)
    }

class BaseCheck:
    def __init__(self, presentation):
        self.presentation = presentation

    def check(self):
        raise NotImplementedError()

    def format_page_link(self, error):
        base_pdf_link = url_for('get_pdf', _id=self.pdf_id)
        page = lambda err: f'{base_pdf_link}#page={str(err)}'
        return [f'<a href="{page(e)}"target="_blank" rel="noopener">{str(e)}<a>' for e in error]
