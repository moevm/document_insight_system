import pytest
import docx
from docx2python import docx2python

from app.main.mse22.document.page_creator import PageCreator
from app.main.mse22.document.page_object import PageObject


@pytest.mark.parametrize("entities, body, paragraph_in_body, paragraph, expected_type, expected_content", [
    (
        [(1, 0, 0)], 0, 0, 0, "paragraph", 0
    ),
    (
        [(2, 0, 0)], 0, 1, 1, "paragraph", 1
    ),
    (
        [(3, 0, 0)], 0, 1, 1, "paragraph", 1
    ),
    (
        [(1, 1, 0), (3, 0, 0)], 2, 1, 2, "paragraph", 1
    ),
    (
        [(0, 1, 0), (2, 0, 0), (1, 0, 0)], 1, 1, 1, "paragraph", 1
    ),
    (
        [(0, 0, 1)], 0, 0, 0, "image", None
    ),
    (
        [(1, 0, 1), (1, 0, 0)], 0, 1, 2, "paragraph", 0
    ),
    (
        [(1, 0, 1)], 0, 0, 1, "image", None
    ),
    (
        [(1, 1, 1)], 2, 0, 1, "image", None
    ),
    (
        [(0, 1, 1)], 1, 0, 0, "image", None
    )
])
def test_make_header(tmp_path, entities, body, paragraph_in_body, paragraph, expected_type, expected_content):
    filename = tmp_path.as_posix() + "/test_document.docx"
    docx_document = docx.Document()
    for pair in entities:
        paragraphs, tables, images = pair
        for i in range(paragraphs):
            docx_document.add_paragraph(str(i))
        for i in range(tables):
            docx_document.add_table(1, 1)
        for i in range(images):
            docx_document.add_picture("../resources/cat.jpg", 432, 540)
    docx_document.save(filename)
    docx2python_document = docx2python(filename)
    page_object = PageCreator.makePageObject(docx2python_document, docx_document,
                                                 body, paragraph_in_body, paragraph)
    assert page_object.type == expected_type
    if page_object.type == "paragraph":
        assert page_object.data.text == str(expected_content)

# Отслеживаемые в PageCreator.make_content() разделы:
checked_sections = ["ВВЕДЕНИЕ", "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ", "ЗАКЛЮЧЕНИЕ"]


@pytest.mark.parametrize("filename, body, paragraph, expected_result", [
    # Список без раздела "Заключение"
    (
        "../test_files/content/list-no-conclusion.docx", 0, 2, (False, None, None)
    ),
    # Список со всеми требуемыми отслеживаемыми разделами (отслеживаемые разделы в содержании капсом)
    (
        "../test_files/content/list-with-mandatory-caps.docx", 0, 2,
        (True, ["Изучение литературы", "Текст 1", "Текст 2"], 8)
    ),
    # Список без некоторых требуемых отслеживаемых разделов (присутствующие отслеживаемые разделы в содержании капсом)
    # (нет переноса строки после содержания)
    (
        "../test_files/content/list-without-mandatory.docx", 0, 2,
        (True, ["Изучение литературы", "Текст 1", "Текст 2"], 7)
    ),
    # Список со всеми требуемыми отслеживаемыми разделами (отслеживаемые разделы в содержании обычным шрифтом)
    (
        "../test_files/content/list-with-mandatory-normal.docx", 0, 2,
        (True, ["Изучение литературы", "Текст 1", "Текст 2"], 8)
    ),
    # Таблица без раздела "Заключение"
    (
        "../test_files/content/table-no-conclusion.docx", 1, 1,
        (False, None, None)
    ),
    # Таблица со всеми требуемыми отслеживаемыми разделами (отслеживаемые разделы в содержании капсом)
    (
        "../test_files/content/table-with-mandatory-caps.docx", 1, 1,
        (True, ["Текущее положение вещей", "Список использованных источников", "Приложение А. Название приложения"], 0)
    ),
    # Таблица без некоторых требуемых отслеживаемых разделов (присутствующие отслеживаемые разделы в содержании капсом)
    (
        "../test_files/content/table-without-mandatory.docx", 1, 1,
        (True, ["Текущее положение вещей", "Список использованных источников", "Приложение А. Название приложения"], 0)
    ),
    # Таблица со всеми требуемыми отслеживаемыми разделами (отслеживаемые разделы в содержании обычным шрифтом)
    (
        "../test_files/content/table-with-mandatory-normal.docx", 1, 1,
        (True, ["Текущее положение вещей", "Список использованных источников", "Приложение А. Название приложения"], 0)
    ),
    # Автосгенерированное содержание
    (
        "../test_files/content/toc.docx", 1, 1,
        (True, ["1. Первый раздел", "1.1. Первый подраздел первого раздела",
                "1.2. Второй подраздел первого раздела", "2. ВТОРОЙ раздел", "2.1. Первый подраздел второго раздела",
                "2.2. Второй подраздел второго раздела"], 0)
    )
])
def test_make_content(filename, body, paragraph, expected_result):
    assert PageCreator.make_content(docx2python(filename), body, paragraph) == expected_result


if __name__ == '__main__':
    pytest.main()
