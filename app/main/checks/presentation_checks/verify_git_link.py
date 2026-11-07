import re

import requests
from lxml import html

from ..base_check import BasePresCriterion, answer


class PresVerifyGitLinkCheck(BasePresCriterion):
    label = 'Проверка действительности ссылок на репозитории'
    _description = 'Проверяет доступность GitHub, GitLab и Bitbucket репозиториев.'
    id = 'verify_git_link'
    REPOSITORY = re.compile(
        r'(?:https?://)?(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)'
        r'/[\w.-]+/[\w.-]+(?:/[\w./-]+)?',
        re.I,
    )

    def __init__(self, file_info, deep_check=False):
        super().__init__(file_info)
        self.deep_check = deep_check
        self.wrong_repo_ref = []
        self.empty_repo_ref = []

    def check(self):
        self.wrong_repo_ref, self.empty_repo_ref = [], []
        errors = []
        texts = self.file.get_text_from_slides()
        for title, text in zip(self.file.get_titles(), texts, strict=True):
            if 'апробация' in title.lower() and re.search(r'репозитор|github|gitlab|bitbucket', text, re.I):
                if not self.REPOSITORY.search(text):
                    errors.append('На слайде «Апробация» нет корректной ссылки на упомянутый репозиторий.')
        urls = list(dict.fromkeys(match.group(0).rstrip('.') for match in self.REPOSITORY.finditer('\n'.join(texts))))
        for url in urls:
            if not url.lower().startswith(('http://', 'https://')):
                url = 'https://' + url
            try:
                response = requests.get(url, timeout=10)
                if response.status_code != 200:
                    self.wrong_repo_ref.append(url)
                elif self.deep_check:
                    self.deep_check_repo(url, response)
            except requests.exceptions.RequestException:
                self.wrong_repo_ref.append(url)
        if self.wrong_repo_ref:
            errors.append('Недоступные репозитории: ' + ', '.join(self.wrong_repo_ref))
        if self.empty_repo_ref:
            errors.append('Пустые репозитории: ' + ', '.join(self.empty_repo_ref))
        return answer(not errors, '<br>'.join(errors) or ('Пройдена!' if urls else 'Нечего проверять!'))

    def deep_check_repo(self, repo, response):
        if 'github.com/' in repo.lower():
            tree = html.fromstring(response.content or b'<html></html>')
            if 'this repository is empty' in tree.text_content().lower():
                self.empty_repo_ref.append(repo)
