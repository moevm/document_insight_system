from app.nlp.similarity_of_texts import check_similarity
from app.utils.get_text_from_slides import get_text_from_slides
from app.utils.parse_for_html import format_header
from app.nlp.stemming import Stemming
from .find_def_sld import FindDefSld
from ..base_check import BasePresCriterion, answer


class FurtherDev(BasePresCriterion):
    label = "Наличие направлений дальнейшего развития"
    description = 'Поиск направления развития в разделе "Заключение"'
    id = 'future_dev'

    def __init__(self, file_info, conclusion='Заключение'):
        super().__init__(file_info)
        self.conclusion = conclusion

    def check(self):
        conclusions = get_text_from_slides(self.file, self.conclusion)
        if conclusions == "":
            return answer(False, 'Заключения не существует')
        
        stemming = Stemming()
        stemming.parse_text(conclusions, False)
        if stemming.find_further_development:
            return answer(True, 'Направления развития найдены')
        else:
            return answer(False, 'Направления развития не найдены в заключении. Попробуйте обозначить их более явной формулировкой, например: "Направления дальнейших исследований"')
