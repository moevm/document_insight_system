import zipfile
import base64
import os
import logging
from typing import Dict, Any

logger = logging.getLogger('latex_unarchiver')

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
        logger.info(f"Инициализация LatexProjectUnarchiver для архива: {path_on_root_of_project}")
        self.path_on_root_of_project = path_on_root_of_project
        self.structure_of_project: Dict[str, Dict[str, Any]] = {}

    def __is_latex_project(self) -> bool:
        """
        Проверяет, является ли архив валидным LaTeX-проектом.
        Условие: должен существовать файл main.tex в корне архива.
        """
        logger.debug("Проверка, является ли архив LaTeX-проектом")
        try:
            with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
                root_candidates = [name for name in zip_ref.namelist() if name.endswith('main.tex')]
                logger.debug(f"Найдено {len(root_candidates)} кандидатов на main.tex")

                for path in root_candidates:
                    parts = path.strip('/').split('/')
                    if len(parts) == 2:  # ETU-latex-template-main/main.tex
                        logger.info(f"Найден main.tex в корне проекта: {path}")
                        return True
                    if len(parts) == 1:  # main.tex
                        logger.info(f"Найден main.tex в корне архива: {path}")
                        return True
                
                logger.warning("Файл main.tex не найден в архиве")
                return False
        except zipfile.BadZipFile:
            logger.error("Ошибка: файл не является ZIP-архивом или поврежден")
            raise ValueError("Файл не является ZIP-архивом или поврежден")

    def __get_file_type(self, filename: str) -> str:
        """Определяет тип файла на основе его расширения."""
        _, ext = os.path.splitext(filename)
        file_type = ALLOWED_EXTENSIONS.get(ext.lower(), 'unknown')
        logger.debug(f"Определение типа файла {filename}: {file_type}")
        return file_type

    def get_project_structure(self) -> Dict[str, Dict[str, Any]]:
        """Возвращает структуру проекта."""
        logger.debug("Запрос структуры проекта")
        return self.structure_of_project

    def check_project_validity(self) -> bool:
        """Проверяет, является ли архив валидным LaTeX-проектом."""
        logger.info("Проверка валидности LaTeX-проекта")
        return self.__is_latex_project()

    def extract_and_decode_project_structure(self) -> None:
        """
        Извлекает файлы из архива, декодирует их в base64 и сохраняет
        структуру проекта, включая только разрешенные файлы.
        """
        logger.info("Начало извлечения и декодирования структуры проекта")
        
        if not self.check_project_validity():
            logger.error("Архив не содержит .tex файлов и не является LaTeX проектом")
            raise ValueError("Архив не содержит .tex файлов и не является LaTeX проектом")

        self.structure_of_project.clear()
        logger.debug("Очищена текущая структура проекта")

        with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
            logger.debug(f"Открыт ZIP-архив: {self.path_on_root_of_project}")
            
            for file_info in zip_ref.infolist():
                if file_info.is_dir():
                    logger.debug(f"Пропуск директории: {file_info.filename}")
                    continue  # Пропускаем только каталоги (сами по себе)

                file_path = file_info.filename
                file_type = self.__get_file_type(file_path)

                if file_type == 'unknown':
                    logger.debug(f"Пропуск файла с неразрешенным расширением: {file_path}")
                    continue  # Игнорируем неразрешенные файлы

                with zip_ref.open(file_path) as file:
                    content = file.read()
                    content_b64 = base64.b64encode(content).decode('utf-8')
                    logger.debug(f"Прочитан и закодирован файл: {file_path} ({len(content)} байт)")

                file_name = os.path.basename(file_path)
                self.structure_of_project[file_path] = {
                    'type': file_type,
                    'content': content_b64,
                    'name': file_name
                }
                logger.info(f"Добавлен файл в структуру проекта: {file_path} (тип: {file_type})")
    
    def save_files_to_folder(self, outdir: str) -> str:
        """
        Сохраняет все файлы из архива в папку.
        """
        logger.info(f"Сохранение файлов из архива в папку: {outdir}")
        
        # Определяем имя папки на основе имени архива (без расширения)
        archive_name = os.path.basename(self.path_on_root_of_project)
        folder_name = os.path.splitext(archive_name)[0]
        
        # Создаем полный путь к папке
        target_folder = os.path.join(outdir, folder_name)
        logger.debug(f"Целевая папка для распаковки: {target_folder}")
        
        # Создаем папку если она не существует
        os.makedirs(target_folder, exist_ok=True)
        logger.debug(f"Создана папка (если не существовала): {target_folder}")
        
        # Извлекаем все файлы
        with zipfile.ZipFile(self.path_on_root_of_project, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
            logger.info(f"Файлы успешно извлечены в: {target_folder}")
            
        return target_folder
        
"""
def logger():
    pass
"""
"""
if __name__ == '__main__':
    # Пример использования
    project_path = 'ETU-latex-template-main.zip'
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
"""