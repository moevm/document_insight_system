from typing import List

from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings
from ...reports.docx_uploader.style import Style


class ReportMainTextCheck(BaseReportCriterion):
    description = "Проверка оформления основного текста отчета"
    id = 'main_text_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = self.file.chapters
        self.preset = 'VKR_MAIN_TEXT' if (self.file_type['report_type'] == 'VKR') else 'LR_MAIN_TEXT'
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
                for child in header["child"]:
                    for index in indexes:
                        if index["index"] > child["number"]:
                            err.append({"child": child["text"], "type": 0})
                            break
                        elif index["index"] == child["number"]:
                            if index["level"] == 3:
                                if child["style"] == 'вкр_подпись для рисунков':
                                    print(child["text"])
                                    break
                                else:
                                    err.append({"child": child["text"], "type": 3})
                                    break
                            elif index["level"] == 4:
                                if child["style"] == 'вкр_подпись таблицы':
                                    print(child["text"])
                                    break
                                else:
                                    err.append({"child": child["text"], "type": 4})
                                    break
                            elif index["level"]:
                                print(child["text"])
                                break
            print(err)
            return answer(0,
                          f'Следующие листы не найдены либо их заголовки расположены не на первой строке новой страницы: <ul><li>{0}</ul>' +
                          'Проверьте очередность листов и орфографию заголовков'+ str(err))

