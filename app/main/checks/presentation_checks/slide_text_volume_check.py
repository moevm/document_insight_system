from ..base_check import BasePresCriterion, answer
from utils import get_text_from_slides
from nlp.stemming import Stemming
import re

WORK_MODE = ["all_slides", "Заключение"]

class SlideTextVolumeCheck(BasePresCriterion):
    label = 'Проверка объема текста на каждом слайде'
    description = 'Объем текста на каждом слайде (за исключением титульного и запасных) должен соответсвовать критериям.'
    id = 'slide_text_volume_check'

    def __init__(self, file_info,  work_mode="all_slides",min_count_words_on_slide=30,
                 min_count_paragraphs=2, min_count_words_in_paragraph=10,
                 max_count_words_on_slide=100, max_count_paragraphs=5,
                 max_count_words_in_paragraph=50,
                 slides_with_required_list=["Цель и задачи", "Заключение"],
                 allow_only_image_or_table=True):
        super().__init__(file_info)
        self.work_mode = work_mode
        self.min_count_words_on_slide = min_count_words_on_slide
        self.min_count_paragraphs = min_count_paragraphs
        self.min_count_words_in_paragraph = min_count_words_in_paragraph
        self.max_count_words_on_slide = max_count_words_on_slide
        self.max_count_paragraphs = max_count_paragraphs
        self.max_count_words_in_paragraph = max_count_words_in_paragraph
        self.slides_with_required_list = slides_with_required_list
        self.allow_only_image_or_table = allow_only_image_or_table

    def check(self):
        result_str = ''
        slides = self.install_work_mode()
        slides_info = []
        if len(slides) == 0:
            return answer(False, 'Презентация пуста или слайды не найдены.')
        for slide in slides:
            title = slide.get_title()
            text = slide.get_text()
            page = slide.get_page_number()[0]
            page_with_images_or_tables = False
            required_list = False
            if "Запасные слайды" in title:
                break
            if title in self.slides_with_required_list:
                required_list = True
            if len(slide.get_images()) > 0 or len(slide.get_table()) > 0:
                page_with_images_or_tables = True
            slides_info.append(self.slide_text_analysis(title, page, text, required_list, page_with_images_or_tables,))
        for slide_info in slides_info:
            res = '' 
            link = self.format_page_link([slide_info['page']])
            if self.allow_only_image_or_table and slide_info['has_image_or_table']:
                continue
            if slide_info['count_words_on_slide'] <= self.min_count_words_on_slide or slide_info['count_words_on_slide'] >= self.max_count_words_on_slide:
                res += f'Количество слов на слайде: {slide_info["count_words_on_slide"]};<br>'
            if slide_info['count_paragraphs'] <= self.min_count_paragraphs or slide_info['count_paragraphs'] >= self.max_count_paragraphs:
                res += f'Количество абзацев на слайде: {slide_info["count_paragraphs"]};<br>'
            paragraphs = slide_info['paragraphs']
            for i in range(len(paragraphs)):
                if paragraphs[i] <= self.min_count_words_in_paragraph or paragraphs[i] >= self.max_count_words_in_paragraph:
                    res += f'Количество слов в абзаце № {i + 1}: {paragraphs[i]};<br>'
            if slide_info['required_list'] and not slide_info['has_list']:
                res += f'На данном слайде наличие списка является обязательным;<br>'
            if res:
                result_str = result_str + f'<br>Слайд {link}:<br>' + res 
        
        if not result_str:
            return answer(True, 'Пройдена!')
        else:
            result_str += f'<br>Количество слов на слайде должно быть больше {self.min_count_words_on_slide} и меньше {self.max_count_words_on_slide};<br>' \
                f'Количество абзацев на слайде должно быть больше {self.min_count_paragraphs} и меньше {self.max_count_paragraphs};<br>' \
                    f'Количество слов в абзаце должно быть больше {self.min_count_words_in_paragraph} и меньше {self.max_count_words_in_paragraph};<br>'
            return answer(False, result_str)
    
    def slide_text_analysis(self, title, page, text, required_list, page_with_images_or_tables):
        if text is None:
            text = '' 
        paragraphs = [p.strip() for p in text.split('\n') if p.strip() and not p.strip().isnumeric() and not p.strip() in title]
        slide_info = {
            'page': page,
            'required_list': required_list,
            'paragraphs': [],
            'count_paragraphs': len(paragraphs),
            'count_words_on_slide': 0,
            'has_list': True,
            'has_image_or_table': page_with_images_or_tables,
            }
        
        for paragraph in paragraphs:
            slide_info['paragraphs'].append(len(paragraph.split()))
            # The variable has_list is currently set to true; after creating the check, set it to false."
        slide_info['count_words_on_slide'] = sum(slide_info['paragraphs'])
        return slide_info
    
    def install_work_mode(self):
        if self.work_mode == WORK_MODE[0]:
            slides = self.file.slides[1:]
        elif self.work_mode == WORK_MODE[1]:
            for slide in self.file.slides:
                if self.work_mode in slide.get_title(): 
                    slides = [slide]
                    break
            stemming = Stemming()
            goal_and_tasks = get_text_from_slides(self.file,"Цель и задачи")
            tasks = stemming.get_sentences(goal_and_tasks, True)
            ignore = re.compile('[0-9][.]?|Задачи:|‹#›')
            cleaned_tasks = [task for task in tasks if not re.fullmatch(ignore, task)]
            task_count = len(cleaned_tasks)
            self.min_count_paragraphs = task_count - 1
            self.max_count_paragraphs = task_count + 3
        else:
            slides = []
        return slides