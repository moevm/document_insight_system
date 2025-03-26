import zipfile
import base64
import os
from typing import Dict, Any

ALLOWED_EXTENSIONS = {
    '.tex': 'latex',
    '.bib': 'bibtex',
    '.cls': 'latex_class',
    '.sty': 'latex_package',
    '.png': 'image',
    '.jpeg': 'image',
    '.jpg': 'image',
    '.svg': 'image',
    '.cfg': 'config',
    '.def': 'definition',
    '.latexmkrc': 'config'
}


class LatexProjectUnarchiver:
    """
    Класс для разархивации и проверки проекта LaTeX.
    """

    def __init__(self, path_on_root_of_project: str):
        self.path_on_root_of_project = path_on_root_of_project
        self.structure_of_project: Dict[str, Dict[str, Any]] = {}

    def __is_latex_project(self) -> bool:
        """Проверяет, содержит ли архив хотя бы один .tex файл."""
        try:
            with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
                for file in zip_ref.namelist():
                    if not file.endswith('/') and os.path.splitext(file)[1].lower() == '.tex':
                        return True
                return False
        except zipfile.BadZipFile:
            raise ValueError("Файл не является ZIP-архивом или поврежден")

    def __get_file_type(self, filename: str) -> str:
        """Определяет тип файла на основе его расширения."""
        _, ext = os.path.splitext(filename)
        return ALLOWED_EXTENSIONS.get(ext.lower(), 'unknown')

    def get_project_structure(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает структуру проекта."""
        return self.structure_of_project

    def check_project_validity(self) -> bool:
        """Проверяет, является ли архив валидным LaTeX-проектом."""
        return self.__is_latex_project()

    def extract_and_decode_project_structure(self) -> None:
        """
        Извлекает файлы из архива, декодирует их в base64 и сохраняет
        структуру проекта, включая только разрешенные файлы.
        """
        if not self.check_project_validity():
            raise ValueError("Архив не содержит .tex файлов и не является LaTeX проектом")

        self.structure_of_project.clear()

        with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    continue  # Пропускаем директории

                file_path = file_info.filename
                file_type = self.__get_file_type(file_path)

                if file_type == 'unknown':
                    continue  # Игнорируем неразрешенные файлы

                with zip_ref.open(file_path) as file:
                    content = file.read()
                    content_b64 = base64.b64encode(content).decode('utf-8')

                file_name = os.path.basename(file_path)
                self.structure_of_project[file_path] = {
                    'type': file_type,
                    'content': content_b64,
                    'name': file_name
                }


# def logger():
#     pass


if __name__ == '__main__':
    # Пример использования
    project_path = 'example_project.zip'
    unarchiver = LatexProjectUnarchiver(project_path)

    try:
        if unarchiver.check_project_validity():
            unarchiver.extract_and_decode_project_structure()
            structure = unarchiver.get_project_structure()
            print("Структура проекта успешно извлечена:")
            for path, data in structure.items():
                print(f"Путь: {path}, Тип: {data['type']}, Имя: {data['name']}")
        else:
            print("Архив не является валидным LaTeX проектом")
    except Exception as e:
        print(f"Ошибка: {e}")