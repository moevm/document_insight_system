import re

from lxml import html
import requests


from ..base_check import BasePresCriterion, answer
# from app.utils.parse_for_html import format_header


class PresIfRefGitHubWork(BasePresCriterion):
    description = "Проверка действительности ссылки на github"
    id = 'if_github'

    def check(self):
        wrong_repo_ref = []
        empty_repo_ref = []
        string_from_text = ''
        text_from_slide = []
        string_result = 'Непройдена! '
        for page, slide in enumerate(self.file.get_text_from_slides(), 1):
            text_from_slide.append(slide)
            string_from_text = ''.join(text_from_slide)
        result = re.findall(
            r'((((((http(s)?://)?(github|gitlab|bitbucket)+)+(.com|.org)+)+/[a-zA-Z0-9_-]+)+/[a-zA-Z0-9_-]+)+/*)+',
            string_from_text)
        if not result:
            return answer(True, 'Нечего проверять!')
        else:
            for i in result:
                try:
                    link = requests.get(i[0])
                    if link.status_code != 200:
                        raise requests.exceptions.ConnectionError
                    tree = html.fromstring(link.content)
                    if not tree.xpath("//a[contains(concat(' ',normalize-space(@class),' '),' tree-item-link ')][contains(@href,'/tree/master/')]/text()"):
                    # @ class ='js-navigation-open Link--primary' or
                        empty_repo_ref.append(i[0])
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                    wrong_repo_ref.append(i[0])
            if wrong_repo_ref and not empty_repo_ref:
                string_result += f"Найдены некорректные ссылки на репозитории! {wrong_repo_ref} ВСЕГО {result}"
                check_result = False
            elif empty_repo_ref and not wrong_repo_ref:
                string_result += f"Найдены пустые репозитории! {empty_repo_ref} ВСЕГО {result}"
                check_result = False
            elif empty_repo_ref and wrong_repo_ref:
                string_result += f"Найдены пустые репозитории! {empty_repo_ref} Также Найдены некорректные репозитории! {wrong_repo_ref} ВСЕГО {result}"
                check_result = False
            else:
                string_result = 'Пройдена!'
                check_result = True
            return answer(check_result, string_result)
