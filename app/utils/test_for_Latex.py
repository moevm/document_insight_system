import zipfile
import base64
import os
from typing import Dict, Any

ALLOWED_EXTENSIONS = {
    '.tex': 'latex',  # LaTeX документ
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
Во вложенном словаре в поле "content" будет хранится содержимое файла в виде Base64-строк
"""

class LatexProjectUnarchiver:
    """
    Класс для разархивации и проверки проекта LaTeX.
    """
    def __init__(self, path_on_root_of_project: str):
        self.path_on_root_of_project = path_on_root_of_project
        self.structure_of_project: Dict[str, Dict[str, Any]] = {}
        self.is_single_tex_file = False

    def __is_latex_project(self) -> bool:
        """
        Проверяет, является ли архив валидным LaTeX-проектом.
        Условие: должен существовать файл main.tex в корне архива.
        """
        if zipfile.is_zipfile(self.path_on_root_of_project):
            try:
                with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
                    root_candidates = [name for name in zip_ref.namelist() if name.endswith('main.tex')]
                    for path in root_candidates:
                        parts = path.strip('/').split('/')
                        if len(parts) == 1 or len(parts) == 2:
                            return True
                    return False
            except zipfile.BadZipFile:
                raise ValueError("Файл поврежден или не является ZIP-архивом")
        return False

    def __is_single_tex_file(self) -> bool:
        """Проверяет, является ли путь одиночным .tex файлом."""
        return os.path.isfile(self.path_on_root_of_project) and self.path_on_root_of_project.endswith('.tex')

    def __get_file_type(self, filename: str) -> str:
        """Определяет тип файла на основе его расширения."""
        _, ext = os.path.splitext(filename)
        return ALLOWED_EXTENSIONS.get(ext.lower(), 'unknown')

    def get_project_structure(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает структуру проекта."""
        return self.structure_of_project

    def check_project_validity(self) -> bool:
        """Проверяет, является ли LaTeX проектом: zip или одиночный tex файл."""
        if self.__is_latex_project():
            self.is_single_tex_file = False
            return True
        if self.__is_single_tex_file():
            self.is_single_tex_file = True
            return True
        return False

    def __process_single_tex_file(self):
        """Обработка одиночного .tex файла."""
        with open(self.path_on_root_of_project, 'rb') as file:
            content = file.read()
            content_b64 = base64.b64encode(content).decode('utf-8')

        file_name = os.path.basename(self.path_on_root_of_project)
        self.structure_of_project[file_name] = {
            'type': 'latex',
            'content': content_b64,
            'name': file_name
        }

    def extract_and_decode_project_structure(self) -> None:
        """
        Извлекает файлы из архива, декодирует их в base64 и сохраняет
        структуру проекта, включая только разрешенные файлы.
        """
        if not self.check_project_validity():
            raise ValueError("Файл не является допустимым LaTeX проектом или .tex файлом")

        self.structure_of_project.clear()

        if self.is_single_tex_file:
            self.__process_single_tex_file()
        else:
            with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.is_dir():
                        continue

                    file_path = file_info.filename
                    file_type = self.__get_file_type(file_path)

                    if file_type == 'unknown':
                        continue

                    with zip_ref.open(file_path) as file:
                        content = file.read()
                        content_b64 = base64.b64encode(content).decode('utf-8')

                    file_name = os.path.basename(file_path)
                    self.structure_of_project[file_path] = {
                        'type': file_type,
                        'content': content_b64,
                        'name': file_name
                    }


if __name__ == '__main__':
    # Пример использования
    project_path = 'ETU-latex-template-main1.zip'
    unarchiver = LatexProjectUnarchiver(project_path)

    try:
        if unarchiver.check_project_validity():
            unarchiver.extract_and_decode_project_structure()
            structure = unarchiver.get_project_structure()
            print("Структура проекта успешно извлечена:")
            print(structure)
            for path, data in structure.items():
                print(f"Путь: {path}, Тип: {data['type']}, Имя: {data['name']}")
        else:
            print("Архив не является валидным LaTeX проектом")
    except Exception as e:
        print(f"Ошибка: {e}")
