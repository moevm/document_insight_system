
import re
import requests
from lxml import html
from urllib.parse import quote

from .find_def_sld import FindDefSld
from ..base_check import BasePresCriterion, answer

#  for check if gitlab-repository is closed:
# GITLAB_URL = 'https://gitlab.com/api/v4'
# PRIVATE_TOKEN = 'glpat-JeZApxShRgB1nsGrMsst'


class PresVerifyGitLinkCheck(BasePresCriterion):
    description = "Проверка действительности ссылки на github"
    id = 'verify_git_link'

    def __init__(self, file_info, deep_check=False):
        super().__init__(file_info)
        self.deep_check = deep_check
        self.wrong_repo_ref = []
        self.empty_repo_ref = []

        self.check_aprb = FindDefSld(file_info=file_info, key_slide="Апробация")
        self.pattern_for_repo = r'((((((http(s)?://)?(github|gitlab|bitbucket)+)+(.com|.org)+)+/[a-zA-Z0-9_-]+)+/[a-zA-Z0-9_-]+)+/*)+'
        self.pattern_for_repo_incorrect = r'\(github\.com\)|\(gitlab\.com\)|\(bitbucket\.org\)|\(github\)|\(gitlab\)|\(bitbucket\)'
        self.pattern_repo_mention = r'репозиторий|репозитория|репозиторию|репозиториев|репозиториям|'

    def check(self):
        string_result = 'Не пройдена!'

        a = self.check_aprb.check()
        page_aprb = ''.join((str(item) for item in self.check_aprb.__getattribute__("found_idxs")))

        text_from_slide = [slide for page, slide in enumerate(self.file.get_text_from_slides(), 1)]
        text_from_slide_aprb = [
            slide.replace(" ", '') for page, slide in enumerate(self.file.get_text_from_slides(), 1)
            if str(page) == page_aprb]

        string_from_text = ' '.join(text_from_slide)
        string_from_text_aprb = ' '.join(text_from_slide_aprb)

        found_repo = re.findall(self.pattern_for_repo, string_from_text)
        found_repo_aprb = re.findall(self.pattern_for_repo, string_from_text_aprb)
        found_repo_aprb_incorrect = re.findall(self.pattern_for_repo_incorrect, string_from_text_aprb)
        print(f'page:{a}, {text_from_slide_aprb}')

        if not found_repo:
            return answer(True, 'Нечего проверять!')
        else:
            if found_repo_aprb_incorrect:
                string_result += f" <br> В слайде 'Апробация' вместо выражений {', '.join([repr(repo) for repo in found_repo_aprb_incorrect])}" \
                                 f" следует привести ссылки вида 'https//github.com/...'"
            if not found_repo_aprb and not found_repo_aprb_incorrect and re.findall(self.pattern_repo_mention, string_from_text_aprb):
                string_result += f' <br> В слайде "Апробация" есть упоминания репозиториев,' \
                                 f'однако ссылки на них либо некорректны, либо отсутствуют.'
            for i in found_repo:
                try:
                    link = requests.get(i[0])
                    if link.status_code != 200:
                        raise requests.exceptions.ConnectionError
                    else:
                        if self.deep_check:
                            self.deep_check_repo(i, link)
                except (requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                    self.wrong_repo_ref.append(i[0])
        if self.wrong_repo_ref and not self.empty_repo_ref:
            string_result += f" <br> Найдены несуществующие или закрытые репозитории: {', '.join([repr(repo) for repo in self.wrong_repo_ref])}"
            check_result = False
        elif self.empty_repo_ref and not self.wrong_repo_ref:
            string_result += f" <br> Найдены пустые репозитории: {', '.join([repr(repo) for repo in self.empty_repo_ref])}"
            check_result = False
        elif self.empty_repo_ref and self.wrong_repo_ref:
            string_result += f" <br> Найдены пустые репозитории: {', '.join([repr(repo) for repo in self.empty_repo_ref])}" \
                             f" <br> Также найдены несуществующие или закрытые репозитории: {', '.join([repr(repo) for repo in self.wrong_repo_ref])}"
            check_result = False
        else:
            string_result = 'Пройдена!'
            check_result = True
        return answer(check_result, string_result)

    def deep_check_repo(self, repo, link):
        if re.findall(r'github', repo[0]):
            tree = html.fromstring(link.content)
            if not tree.xpath("//a[@class ='js-navigation-open Link--primary']"):
                self.empty_repo_ref.append(repo[0])

        # if re.findall(r'gitlab', i[0]):
        #     project_id = quote(i[0].replace('https://gitlab.com/', ''), safe='')
        #     url = f'{GITLAB_URL}/projects/{project_id}?private_token={PRIVATE_TOKEN}'
        #     response = requests.get(url)
        #     project_info = response.json()
        #     if project_info['visibility'] == 'private':
        #         wrong_repo_ref.append(i[0])
