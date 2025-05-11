import os
import re
import logging 


logger = logging.getLogger('root_logger')

class LatexProcessor():
    """
    Класс для объединения файлов LaTeX в один документ.
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
    
    def _process_file(self, file_path: str, base_path: str) -> str:
        if not os.path.exists(file_path):
            logger.warning(f"File {file_path} not found!")
            return ""
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        content = self._replace_documentclass(content, base_path)
        content = self._replace_imports(content, base_path)
        return content
        
    def _replace_documentclass(self, content: str, base_path: str) -> str:
        pattern = re.compile(r"\\documentclass\[.*?\]\{(.*?)\}")
        match = pattern.search(content)
        
        if match:
            cls_name = match.group(1).strip()
            cls_file = os.path.join(base_path, f"{cls_name}.cls")
            
            if os.path.exists(cls_file):
                with open(cls_file, "r", encoding="utf-8") as f:
                    cls_content = f.read()
                cls_content = re.escape(cls_content)
                content = pattern.sub(cls_content, content)
        return content
    
    def _replace_imports(self, content: str, base_path: str) -> str:
        pattern = re.compile(r"\\(?:include|input)\{([^}]+)\}")

        def replace(match):
            relative_path = match.group(1).strip()
            if not relative_path.endswith(".tex"):
                relative_path += ".tex"
            file_path = os.path.join(base_path, relative_path)
            return self._process_file(file_path, base_path)

        return pattern.sub(replace, content)


# Пример использования
'''
if __name__ == "__main__":
    project_dir = "path_to_unzipped_folder"
    output_file = "output.tex"
    merger = LatexProcessor()
    merger.merge_latex_project(project_dir, output_file)
'''
