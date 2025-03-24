from abc import ABC, abstractmethod

class LatexProcessor(ABC):
    """
    Класс для обработки проектов LaTeX.
    """

    @abstractmethod
    def merge_latex_project(self, project_path: str, output_file: str) -> None:
        """
        Объединяет проект LaTeX в единый файл для дальнейшей обработки.

        :param project_path: Путь к директории с LaTeX-проектом.
        :param output_file: Путь к итоговому объединенному файлу.
        """
        pass