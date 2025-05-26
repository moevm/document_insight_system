import re
import os
import base64
import logging
from typing import Dict, Any

logger = logging.getLogger('root_logger')

class LatexProcessor:
    """
    Класс для объединения файлов LaTeX в один документ,
    используя структуру проекта в виде словаря.
    """

    def merge_latex_project(
        self,
        project_structure: Dict[str, Dict[str, Any]],
        output_file: str
    ) -> None:
        """Объединяет проект LaTeX в один файл."""
        logger.info("Начало объединения LaTeX-проекта...")
        
        main_path = self._find_main_tex(project_structure)
        if not main_path:
            logger.error("ОШИБКА: Файл main.tex не найден. Проверьте структуру проекта.")
            raise ValueError("main.tex не найден.")

        logger.info(f"Основной файл найден: {main_path}")
        logger.info("Обработка основного файла и его зависимостей...")
        merged_content = self._process_file(main_path, project_structure)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(merged_content)
        logger.info(f"УСПЕХ: Проект сохранён в файл {output_file}")

        return output_file

    def _find_main_tex(self, structure: Dict[str, Dict[str, Any]]) -> str:
        """Ищет main.tex в структуре проекта."""
        logger.info("Поиск файла main.tex...")
        for path in structure:
            if path.endswith("main.tex"):
                logger.info(f"Найден main.tex: {path}")
                return path
        logger.warning("main.tex не найден среди файлов проекта.")
        return ""

    def _decode_content(self, base64_content: str) -> str:
        """Декодирует содержимое файла из base64."""
        logger.debug("Декодирование содержимого файла...")
        return base64.b64decode(base64_content).decode('utf-8')

    def _process_file(self, file_path: str, structure: Dict[str, Dict[str, Any]]) -> str:
        """Обрабатывает файл и заменяет зависимости."""
        logger.info(f"Чтение файла: {file_path}")
        if file_path not in structure:
            logger.error(f"ФАЙЛ НЕ НАЙДЕН: {file_path} отсутствует в проекте.")
            return ""

        content = self._decode_content(structure[file_path]['content'])
        logger.info("Поиск и замена documentclass...")
        content = self._replace_documentclass(content, structure)
        logger.info("Поиск и замена подключённых файлов (include/input)...")
        content = self._replace_imports(content, structure, file_path)
        return content

    def _replace_documentclass(self, content: str, structure: Dict[str, Dict[str, Any]]) -> str:
        """Заменяет \documentclass на содержимое .cls-файла."""
        pattern = re.compile(r"\\documentclass\[.*?\]\{(.*?)\}")
        match = pattern.search(content)

        if match:
            cls_name = match.group(1).strip()
            logger.info(f"Найден documentclass: {cls_name}")
            cls_file_path = next((p for p in structure if p.endswith(f"{cls_name}.cls")), None)
            if cls_file_path:
                logger.info(f"Файл класса найден: {cls_file_path}")
                cls_content = self._decode_content(structure[cls_file_path]['content'])
                content = pattern.sub(cls_content, content)
            else:
                logger.warning(f"ПРЕДУПРЕЖДЕНИЕ: Файл класса {cls_name}.cls не найден.")
        else:
            logger.debug("documentclass не обнаружен в файле.")
        return content

    def _replace_imports(self, content: str, structure: Dict[str, Dict[str, Any]], current_path: str) -> str:
        """Заменяет \include и \input на содержимое подключённых файлов."""
        pattern = re.compile(r"\\(?:include|input)\{([^}]+)\}")

        def replace(match):
            relative_path = match.group(1).strip()
            if not relative_path.endswith(".tex"):
                relative_path += ".tex"

            base_dir = "/".join(current_path.split("/")[:-1])
            full_path = os.path.normpath(os.path.join(base_dir, relative_path)).replace("\\", "/")

            logger.info(f"Обработка подключения: {relative_path} (полный путь: {full_path})")
            return self._process_file(full_path, structure)

        return pattern.sub(replace, content)
    
    
# Пример использования
'''
if __name__ == "__main__":
    project_structure = dict()
    output_file = "output.tex"
    merger = LatexProcessor()
    merger.merge_latex_project(project_structure, output_file)
'''