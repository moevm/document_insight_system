import re

import lxml
import requests
from lxml import html

from ..base_check import BasePresCriterion, answer
from app.utils.parse_for_html import format_header

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
        result = re.findall(r'(((((http(s)?://)?(github|gitlab|bitbucket)+)+(.com|.org)+)+/\w+)+/\w+)+', string_from_text)
        if not result:
            return answer(True, 'Нечего проверять!')
        else:
            for i in result:
                try:
                    page = requests.get(i[0])
                    if page.status_code != 200:
                        raise requests.exceptions.ConnectionError
                    tree = lxml.html.fromstring(page.content)
                    file_and_folders = tree.xpath('//*[@class="js-navigation-open"]')
                    if not file_and_folders:
                        empty_repo_ref.append(i[0])
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                    wrong_repo_ref.append(i[0])
            if wrong_repo_ref:
                string_result += f"Найдены некорректные ссылки на репозитории! {wrong_repo_ref}"
                if empty_repo_ref:
                    string_result += f", Также Найдены пустые репозитории! {empty_repo_ref}"
            elif empty_repo_ref:
                string_result += f"Найдены пустые репозитории! {empty_repo_ref}"
            else:
                string_result = 'Пройдена!'
            return answer(True, string_result)