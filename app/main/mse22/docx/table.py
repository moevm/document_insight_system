class Cell:
    def __init__(self, cell, paragraphs):
        self.ceil_paragraphs = paragraphs
        self.cell_text = cell.text
        self.cell_vertical_alignment = cell.vertical_alignment
        self.cell_width = cell.width


class Table:
    def __init__(self, table, cells):
        self.table_cells = cells
        self.table_alignment = table.alignment
        self.table_autofit = table.autofit
        self.table_direction = table.table_direction
