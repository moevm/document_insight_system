import pymorphy2

morph = pymorphy2.MorphAnalyzer()

def answer(mod, *args):
    return {
        'score': float(mod),
        'verdict': args
    }


class BaseCheck:
    description = None
    file_type = None
    id = None

    def __init__(self, file_info):
        self.file = file_info.get('file')
        self.filename = file_info.get('filename', '')
        self.pdf_id = file_info.get('pdf_id')

    def check(self):
        raise NotImplementedError()

    def format_page_link(self, error):
        base_pdf_link = f'/get_pdf/{self.pdf_id}'
        page = lambda err: f'{base_pdf_link}#page={str(err)}'
        return [f'<a href="{page(e)}"target="_blank" rel="noopener">{str(e)}<a>' for e in error]

    @property
    def name(self):
        return self.description


class BasePresCriterion(BaseCheck):
    file_type = 'pres'


class BaseReportCriterion(BaseCheck):
    file_type = 'report'
