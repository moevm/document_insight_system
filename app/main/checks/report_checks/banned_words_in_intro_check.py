import re

from ..base_check import BaseReportCriterion, answer, morph

EXAMPLE_BANNED_WORDS = ["добрый", "хабр", "habr"]
EXAMPLE_TARGET_CHAPTER = "введение"
EXAMPLE_TARGET_CHAPTER_CHILDS = ["объект исследования", "предмет исследования"]


class BannedWordsInIntroCheck(BaseReportCriterion):
    label = "Проверка наличия запрещенных слов во введении"
    _description = label
    id = "banned_words_in_intro"
    priority = True

    def __init__(self, file_info, banned_words=None, target_chapter=None, target_chapter_childs=None):
        super().__init__(file_info)
        if banned_words:
            self.banned_words = {morph.normal_forms(word)[0] for word in banned_words}
        else:
            self.banned_words = {morph.normal_forms(word)[0] for word in EXAMPLE_BANNED_WORDS}

        self.chapters = self.file.make_chapters(work_type="VKR")
        self.target_chapter = target_chapter if target_chapter else EXAMPLE_TARGET_CHAPTER
        self.target_chapter_childs = (
            [s.lower() for s in target_chapter_childs] if target_chapter_childs else EXAMPLE_TARGET_CHAPTER_CHILDS
        )
        self.errors = []

    def check(self):
        self.intro = {}

        for chapter in self.chapters:
            header: str = chapter["text"].lower()
            if header.find(self.target_chapter.lower()) >= 0:
                self.intro = chapter
                break

        if not self.intro:
            return answer(False, f"Нет раздела {self.target_chapter}")

        for child in self.intro["child"]:
            for target_child in self.target_chapter_childs:
                if target_child in child["text"].lower():
                    self._check_chapter(child)

        if self.errors:
            fail_text = f"Есть запрещенные слова в {self.target_chapter}: " + ", ".join(self.errors)
            return answer(False, fail_text)
        return answer(True, "Проверка пройдена")

    def _check_chapter(self, child):
        words = re.split(r"\W+", child["text"].lower())
        for ban_word in self.banned_words:
            if ban_word in words:
                self.errors.append(ban_word)
