from docx2python import docx2python
import docx
import re

from app.main.mse22.document.page_object import PageObject
from app.main.mse22.document.page import Page


class PageCreator:
    def createPageObjects(self, path):
        docx_docx2python = docx2python(path)
        indices = self.makeIndices(docx_docx2python)
        if not indices[0]:
            return 'Report does not contain a section' + indices[1]
        image_pattern = r'\-{4}media/image\d+\.\D+\-{4}'
        chapters = ['Титульный лист', 'Цель работы', 'Основные теоретические положения', 'Выполнение работы',
                    'Тестирование', 'Выводы']
        docx_docx = docx.Document(path)
        table_index = 0
        paragraph_index = 0
        page_objects = []
        current_page_object = []
        for i in range(0, len(indices[1])):
            for j in range(indices[1][i][0][0], indices[1][i][1][0] + 1):
                if len(docx_docx2python.body[j]) > 1:
                    current_page_object.append(PageObject('table', docx_docx.tables[table_index]))
                    table_index += 1
                else:
                    if indices[1][i][0][0] == indices[1][i][1][0]:
                        for _ in range(indices[1][i][0][1], indices[1][i][1][1] + 1):
                            if re.search(image_pattern, docx_docx2python.body[j][0][0][_ - 1]):
                                current_page_object.append(PageObject('image', docx_docx.paragraphs[paragraph_index]))
                            else:
                                current_page_object.append(PageObject('paragraph',
                                                                      docx_docx.paragraphs[paragraph_index]))
                            paragraph_index += 1
                    elif j == indices[1][i][0][0] and j != indices[1][i][1][0]:
                        for _ in range(indices[1][i][0][1], len(docx_docx2python.body[j][0][0])):
                            if re.search(image_pattern, docx_docx2python.body[j][0][0][_ - 1]):
                                current_page_object.append(PageObject('image', docx_docx.paragraphs[paragraph_index]))
                            else:
                                current_page_object.append(PageObject('paragraph',
                                                                      docx_docx.paragraphs[paragraph_index]))
                            paragraph_index += 1
                    elif j != indices[1][i][0][0] and j != indices[1][i][1][0]:
                        for _ in range(0, len(docx_docx2python.body[j][0][0])):
                            if re.search(image_pattern, docx_docx2python.body[j][0][0][_ - 1]):
                                current_page_object.append(PageObject('image', docx_docx.paragraphs[paragraph_index]))
                            else:
                                current_page_object.append(PageObject('paragraph',
                                                                      docx_docx.paragraphs[paragraph_index]))
                            paragraph_index += 1
                    elif j == indices[1][i][1][0]:
                        for _ in range(0, indices[1][i][1][0] + 1):
                            if re.search(image_pattern, docx_docx2python.body[j][0][0][_ - 1]):
                                current_page_object.append(PageObject('image', docx_docx.paragraphs[paragraph_index]))
                            else:
                                current_page_object.append(PageObject('paragraph',
                                                                      docx_docx.paragraphs[paragraph_index]))
                            paragraph_index += 1

            page_objects.append(Page(chapters[i], current_page_object))
            current_page_object = []

        return page_objects

    def makeIndices(self, doc_result):
        i_start = [0, 0]
        chapters = ['Цель работы', 'Основные теоретические положения', 'Выполнение работы', 'Тестирование', 'Выводы']
        docx_chapters = []
        cur_index = 0
        cur_chapter = 0
        while cur_chapter != len(chapters):
            if cur_index >= len(doc_result.body):
                return [False, chapters[cur_chapter]]
            if len(doc_result.body[cur_index]) > 1:
                cur_index += 1
            elif chapters[cur_chapter] in doc_result.body[cur_index][0][0]:
                tmp_i_end = [0, 0]
                tmp_i_start = i_start.copy()
                tmp_i_end[0] = cur_index
                tmp_i_end[1] = doc_result.body[cur_index][0][0].index(chapters[cur_chapter]) - 1
                docx_chapters.append([tmp_i_start, tmp_i_end])
                i_start[0] = cur_index
                i_start[1] = doc_result.body[cur_index][0][0].index(chapters[cur_chapter])
                cur_chapter += 1
            else:
                cur_index += 1
        docx_chapters.append([[cur_index, docx_chapters[len(docx_chapters) - 1][1][1] + 1],
                              [len(doc_result.body) - 1, len(doc_result.body[len(doc_result.body) - 1][0][0])]])
        return [True, docx_chapters]
