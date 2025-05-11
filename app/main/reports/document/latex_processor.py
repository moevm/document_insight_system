import re
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
        main_path = self._find_main_tex(project_structure)
        if not main_path:
            logger.error("main.tex не найден в структуре проекта.")
            raise ValueError("main.tex не найден.")

        merged_content = self._process_file(main_path, project_structure)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(merged_content)
        logger.info(f"Merged LaTeX project saved to {output_file}")

    def _find_main_tex(self, structure: Dict[str, Dict[str, Any]]) -> str:
        for path in structure:
            if path.endswith("main.tex"):
                return path
        return ""

    def _decode_content(self, base64_content: str) -> str:
        return base64.b64decode(base64_content).decode('utf-8')

    def _process_file(self, file_path: str, structure: Dict[str, Dict[str, Any]]) -> str:
        if file_path not in structure:
            logger.warning(f"Файл {file_path} не найден в структуре проекта.")
            return ""

        content = self._decode_content(structure[file_path]['content'])
        content = self._replace_documentclass(content, structure)
        content = self._replace_imports(content, structure, file_path)
        return content

    def _replace_documentclass(self, content: str, structure: Dict[str, Dict[str, Any]]) -> str:
        pattern = re.compile(r"\\documentclass\[.*?\]\{(.*?)\}")
        match = pattern.search(content)

        if match:
            cls_name = match.group(1).strip()
            cls_file_path = next((p for p in structure if p.endswith(f"{cls_name}.cls")), None)
            if cls_file_path:
                cls_content = self._decode_content(structure[cls_file_path]['content'])
                content = pattern.sub(cls_content, content)
            else:
                logger.warning(f"Класс {cls_name}.cls не найден в проекте.")
        return content

    def _replace_imports(self, content: str, structure: Dict[str, Dict[str, Any]], current_path: str) -> str:
        pattern = re.compile(r"\\(?:include|input)\{([^}]+)\}")

        def replace(match):
            relative_path = match.group(1).strip()
            if not relative_path.endswith(".tex"):
                relative_path += ".tex"

            base_dir = "/".join(current_path.split("/")[:-1])
            full_path = os.path.normpath(os.path.join(base_dir, relative_path)).replace("\\", "/")

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
