import os
import re


class LatexProcessor():
    """
    Класс для объединения файлов LaTeX в один документ.
    """
    
    def merge_latex_project(self, project_path: str, output_file: str) -> None:
        main_file = os.path.join(project_path, "main.tex")
        merged_content = self._process_file(main_file, project_path)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(merged_content)
        print(f"Merged LaTeX project saved to {output_file}")
    
    def _process_file(self, file_path: str, base_path: str) -> str:
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} not found!")
            return ""
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        content = self._replace_imports(content, base_path)
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
