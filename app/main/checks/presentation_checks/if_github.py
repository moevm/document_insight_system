import re
import os
import subprocess

from lxml import html
import requests

from .find_def_sld import FindDefSld

from ..base_check import BasePresCriterion, answer
# from app.utils.parse_for_html import format_header


class PresIfRefGitHubWork(BasePresCriterion):
    description = "Проверка действительности ссылки на github"
    id = 'if_github'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.check_apr = FindDefSld(file_info=file_info, key_slide="Апробация")



    def check(self):
        wrong_repo_ref = []
        empty_repo_ref = []
        string_from_text = ''
        text_from_slide = []
        text_from_slide_apr = []
        string_result = 'Не пройдена! '
        string_from_text_aprob = ''
        page_ap = ''

        found_slides_result = self.check_apr.check()
        found_slides_result_2 = self.check_apr.__getattribute__("found_idxs")
        for item in found_slides_result_2:
            page_ap += str(item)

        for page, slide in enumerate(self.file.get_text_from_slides(), 1):
            slide.replace(" ", '')
            text_from_slide.append(slide)
            string_from_text = ' '.join(text_from_slide)

            if str(page) == page_ap:
                text_from_slide_apr.append(slide.replace(" ", ''))
                string_from_text_aprob = ' '.join(text_from_slide_apr)

        result = re.findall(r'((((((http(s)?://)?(github|gitlab|bitbucket)+)+(.com|.org)+)+/[a-zA-Z0-9_-]+)+/[a-zA-Z0-9_-]+)+/*)+', string_from_text)
        result_2 = re.findall(
            r'\(github\.com\)|\(gitlab\.com\)|\(bitbucket\.org\)|\(github\)|\(gitlab\)|\(bitbucket\)',
            string_from_text_aprob)

        # return answer(True, result, result_2)
        if not result:
            return answer(True, 'Нечего проверять!')
        else:
            if result_2:
                string_result += f" Вместо выражений {result_2} следует привести ссылки вида 'https//github.com/...'"
            for i in result:
                try:
                    link = requests.get(i[0])
                    if link.status_code != 200:
                        raise requests.exceptions.ConnectionError
                    git_link = i[0]+'.git'
                    local_dir_name = '~/src/2/git_l'
                    subprocess.run(["git", "clone", git_link, local_dir_name])
                    if os.path.exists(local_dir_name):
                        contents = os.listdir(local_dir_name)
                        if len(contents) == 0:
                            empty_repo_ref.append(i[0])

                    # tree = html.fromstring(link.content)
                    # if not tree.xpath("//a[@class ='js-navigation-open Link--primary']"):
                    #     empty_repo_ref.append(i[0])
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                    wrong_repo_ref.append(i[0])
        if wrong_repo_ref and not empty_repo_ref:
            string_result += f"Найдены нерабочие ссылки на репозитории: {wrong_repo_ref}"
            check_result = False
        elif empty_repo_ref and not wrong_repo_ref:
            string_result += f"Найдены пустые репозитории: {empty_repo_ref}"
            check_result = False
        elif empty_repo_ref and wrong_repo_ref:
            string_result += f"Найдены пустые репозитории: {empty_repo_ref} Также найдены нерабочие репозитории: {wrong_repo_ref}"
            check_result = False
        else:
            string_result = 'Пройдена!'
            check_result = True
        return answer(check_result, string_result)
