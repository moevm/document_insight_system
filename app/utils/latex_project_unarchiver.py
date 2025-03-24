import zipfile
import base64
import os
from typing import Dict, Any


ALLOWED_EXTENSIONS = {
    '.tex': 'latex',  # LaTeX документ
    '.bib': 'bibtex',  # База данных библиографии
    '.cls': 'latex_class',  # Файл класса LaTeX
    '.sty': 'latex_package',  # Пакет LaTeX
    '.png': 'image',  # Изображение
    '.jpeg': 'image',  # Изображение
    '.jpg': 'image',  # Изображение
    '.svg': 'image',  # Изображение
    '.cfg': 'config',  # Файл конфигурации
    '.def': 'definition',  # Файл с определениями макросов
    '.latexmkrc': 'config'  # Конфигурация для latexmk
}


"""
Структура данных - словарь, где ключи это путь до файла, а значения - словарь с данными о файле.

Пример:
project_structure = {
    "path/to/main.tex": {
        "type": "latex",
        "content": "Содержимое файла main.tex",
        "name": "main.tex"
    },
    "path/to/image.png": {
        "type": "image",
        "content": "Содержимое файла image.png",
        "name": "image.png"
    }
}

Во вложенном словаре в поле "content" будет хранится содержимое файла в виде Base64-строк.
"""


class LatexProjectUnarchiver:
    """
    Класс для разархивации и проверки проекта LaTeX.
    """

    def __init__(self, path_on_root_of_project: str):
        self.path_on_root_of_project = path_on_root_of_project
        self.structure_of_project: Dict[str, Dict[str, Any]] = {}

    def __is_latex_project(self):
        """Проверка на LaTeX-проект."""
        return True

    def __get_file_type(self, filename):
        """Возвращает тип файла."""
        return "type_of_file"

    def get_project_structure(self):
        """Возвращает структуру проект в виде словаря."""
        return "file_structure"

    def check_project_validity(self):
        """Проверяет корректность проекта в архиве."""
        return True

    def extract_and_decode_project_structure(self):
        """Извлекает файлы из архива, декодирует и фильтрует их"""
        pass


def logger():
    pass



if __name__ == '__main__':
    logger()