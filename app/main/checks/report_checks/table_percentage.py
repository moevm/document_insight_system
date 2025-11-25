import fitz
from docx import Document
from ..base_check import BaseReportCriterion, answer

default_font_size: int = 12 # Значение размера шрифта по умолчанию
default_line_spacing: float = 1.0 # Значение межстрочного интервала по умолчанию
chars_per_line: int = 20 # Примерное кол-во символов в строке ячейки
cell_padding = 5 # Примерный размер отступов от границ ячейки
row_padding = 2 # Примерное расстояние между строками таблиц

#С данными значениями погрешность 4-5 процентов

class TablePercentage(BaseReportCriterion):
    label = "Проверка процентного соотношения таблиц в документе"
    description = "Проверяет, что таблицы занимают не более установленного процента площади документа"
    id = 'table_percentage'


    def __init__(self, file_info, hasApplication = True,max_percentage = 30):
        super().__init__(file_info)
        self._max_percentage = max_percentage
        self._hasApplication = hasApplication

    def get_font_size(self, run, paragraph) -> float:
        """Функция получения размера шрифта"""
        if run.font.size:
            return run.font.size.pt
        elif run.style and run.style.font.size:
            return run.style.font.size.pt
        elif paragraph.style and paragraph.style.font.size:
            return paragraph.style.font.size.pt
        else:
            return default_font_size

    def heightCell(self, cell) -> float:
        """Функция получения высоты ячейки"""
        total_height = 0

        for paragraph in cell.paragraphs:
            line_count = 1

            text_length = len(paragraph.text)
            if text_length > 0:
                line_count = max(1, (text_length + chars_per_line - 1) // chars_per_line)

            max_font_size = default_font_size
            for run in paragraph.runs:
                font_size = self.get_font_size(run, paragraph)
                max_font_size = max(max_font_size, font_size)

            line_spacing = default_line_spacing

            paragraph_height = line_count * max_font_size * line_spacing
            total_height += paragraph_height

            if paragraph.paragraph_format.space_after:
                total_height += paragraph.paragraph_format.space_after.pt
            if paragraph.paragraph_format.space_before:
                total_height += paragraph.paragraph_format.space_before.pt

        total_height += 2 * cell_padding

        return total_height

    def heightTable(self, table) -> float:
        """Функция получения высоты таблицы"""
        total_height = 0
        for row in table.rows:
            if row.height:
                total_height += row.height.pt
            else:
                heights = []
                for cell in row.cells:
                    heights.append(self.heightCell(cell))
                total_height += max(heights) if heights else 0

            total_height += row_padding

        return total_height

    def getPercentOfTables(self) -> float:
        """Функция получение процента таблиц в документе"""
        doc_docx = self.file.file

        page_count = self.file.page_counter()
        if page_count == 0:
            return 0

        section = doc_docx.sections[0]
        page_height = section.page_height.pt
        total_height = page_height * page_count

        if total_height == 0:
            return 0

        tables_height = 0

        end_index = len(doc_docx.tables)

        if self._hasApplication:
            end_index = self.find_table_index_after_text('ПРИЛОЖЕНИЕ')
            end_index = end_index if end_index is not None else len(doc_docx.tables)

        for table_index, table in enumerate(doc_docx.tables):
            if table_index < end_index:
                table_height = self.heightTable(table)
                tables_height += table_height

        percentage = (tables_height / total_height) * 100
        return percentage


    def find_table_index_after_text(self, target_text: str) -> int | None:
        """Функция находит первый индекс таблицы после target_text, если не найден, то вернет None"""
        doc_docx = self.file.file
        for i, paragraph in enumerate(doc_docx.paragraphs):
            if target_text in paragraph.text:

                para_elem = paragraph._element
                following_tables = para_elem.xpath('./following-sibling::w:tbl')

                for table_elem in following_tables:

                    for index, table in enumerate(doc_docx.tables):
                        if table._element == table_elem:
                            return index

        return None

    def find_tables_indexs_between_text(self,start_text: str, end_text: str | None = None):
        """Функция нахождения индексов начала и конца таблиц между двумя текстами"""
        start_index = self.find_table_index_after_text(start_text)
        end_index = self.find_table_index_after_text(end_text)

        return (start_index, end_index)

    def check(self):
        try:
            if self.file.page_counter() < 4:
                return answer(False, "В отчете недостаточно страниц. Нечего проверять.")

            percent_tables = self.getPercentOfTables()

            if percent_tables <= self._max_percentage:
                return answer(
                    True,
                    "Пройдена!"
                )
            else:
                return answer(
                    False,
                    f'''
                    Таблицы занимают {percent_tables:.1f}% документа, что превышает допустимые {self._max_percentage}%.
                    Рекомендации:
                    <ul>
                        <li>Уменьшите количество таблиц в основном тексте документа;</li>
                        <li>Перенесите вспомогательные таблицы в приложения;</li>
                        <li>Сократите объем данных в таблицах, оставив только самую важную информацию.</li>
                    </ul>
                    '''
                )
        except Exception as e:
            return answer(False, f"Ошибка при проверке процентного соотношения таблиц: {str(e)}")

