from typing import List

from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings
from ...reports.docx_uploader.style import Style

class ReportHeaders(BaseReportCriterion):
    description = "Проверка оформления заголовков отчета"
    id = 'header_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = self.file.chapters
        self.preset = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.styles: List[Style] = []
        presets = StyleCheckSettings.CONFIGS.get(self.preset)
        prechecked_props_lst = StyleCheckSettings.PRECHECKED_PROPS
        for format_description in presets:
            prechecked_dict = {key: format_description["style"].get(key) for key in prechecked_props_lst}
            style = Style()
            style.__dict__.update(prechecked_dict)
            self.styles.append(style)

    def check(self):
        err = []
        if self.file_type['report_type'] == 'VKR':
            indexes = self.file.build_vkr_hierarchy(self.styles)
            print(indexes)
            for header in self.headers:
                print(header["text"])
                print(header["number"])
                for index in indexes:
                    if index["index"] > header["number"]:
                        err.append({"header": header["text"], "type": 0})
                        break
                    elif index["index"] == header["number"]:
                        if index["level"] == 1:
                            if header["style"] == 'heading 2':
                                print(index["text"])
                                break
                            else:
                                err.append({"header": header["text"], "type": 1})
                                break
                        if index["level"] == 2:
                            if index["text"]:
                                print(index["text"])
                                break
                            else:
                                err.append({"header": header["text"], "type": 2})
                                break
            print(err)
        return answer(0,
                          f'Следующие листы не найдены либо их заголовки расположены не на первой строке новой страницы: <ul><li>{0}</ul>' +
                          'Проверьте очередность листов и орфографию заголовков' + str(self.file.chapters) + str(err))

