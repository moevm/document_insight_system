import re
from enum import Enum

class DocumentType(Enum):
    REPORT = 'report'
    PRESENTATION = 'pres'

class DecimalPlacesChecker:
    """
    Класс для проверки чисел на избыточное количество десятичных знаков.    
    Игнорирует IP-адреса, версии ПО и другие составные числа.

    Проверяет:
    - Обычные числа с десятичными знаками (например, -3.14159)
    Не проверяет:
    - IP-адреса (например, 192.168.1.1)
    - Версии ПО (например, 1.2.3.4)
    - Другие составные числа
    """
    
    DECIMAL_PATTERN = r'(?<!\d)(?<!\.)-?\d+[.,]\d+(?!\d)'
    
    def __init__(self, max_decimal_places=2, type=DocumentType.REPORT):
        self.max_decimal_places = max_decimal_places
        self.type = type
    
    def is_valid_number(self, match, text):
        start_pos = match.start()
        end_pos = match.end()
        
        char_before = text[start_pos - 1] if start_pos > 0 else ' '
        
        if char_before == '.':
            return False
        
        if end_pos < len(text):
            char_after = text[end_pos]
            if char_after == '.' and end_pos + 1 < len(text) and text[end_pos + 1].isdigit():
                return False
        
        return True
    
    def count_decimal_places(self, number_str):
        normalized = number_str.replace(',', '.')
        
        if '.' in normalized:
            decimal_part = normalized.split('.')[1]
            return len(decimal_part)
        
        return 0
    
    def has_excessive_decimals(self, number_str):
        return self.count_decimal_places(number_str) > self.max_decimal_places
    
    def find_violations_in_text(self, text):
        violations = []
        matches = re.finditer(self.DECIMAL_PATTERN, text)
        
        for match in matches:
            if not self.is_valid_number(match, text):
                continue
            
            number_str = match.group()
            decimal_places = self.count_decimal_places(number_str)
            
            if decimal_places > self.max_decimal_places:
                violations.append((number_str, decimal_places, match))
        
        return violations
    
    def find_violations_in_lines(self, lines):
        violations = []
        
        for line_idx, line in enumerate(lines):
            line_violations = self.find_violations_in_text(line)
            
            for number_str, decimal_places, match in line_violations:
                violations.append((line_idx, number_str, decimal_places, line))
        
        return violations
    
    def highlight_number(self, line, number_str):
            return line.replace(number_str, f'<b>{number_str}</b>', 1)
    
    def format_violation_message(self, line_idx, line, number_str, decimal_places):
        highlighted_line = self.highlight_number(line, number_str)
        return (
            f'Строка {line_idx + 1}: {highlighted_line} '
            f'<i>(найдено {decimal_places} знаков после запятой, '
            f'максимум: {self.max_decimal_places})</i>'
        )
    
    def format_success_message(self):
        if self.type == DocumentType.REPORT:
            document_type = "документе"
        elif self.type == DocumentType.PRESENTATION:
            document_type = "презентации"
        return (
            f'Проверка пройдена! Все числа в {document_type} имеют допустимое количество '
            f'десятичных знаков (не более {self.max_decimal_places}).'
        )
    
    def format_failure_message(self, total_violations, 
                               violations_by_location, 
                               format_page_link_fn=None):
        if self.type == DocumentType.REPORT:
            location_label = "Страница"
        elif self.type == DocumentType.PRESENTATION:
            location_label = "Слайд"
        result_str = (
            f'<b>Найдены числа с избыточным количеством десятичных знаков!</b><br>'
            f'Максимально допустимое количество знаков после запятой: {self.max_decimal_places}<br>'
            f'Всего нарушений: {total_violations}<br><br>'
        )
        
        for location_num, violations in violations_by_location.items():
            if format_page_link_fn:
                location_str = f'{location_label} {format_page_link_fn([location_num])}'
            else:
                location_str = f'{location_label} №{location_num}'
            
            result_str += f'<b>{location_str}:</b><br>'
            result_str += '<br>'.join(violations)
            result_str += '<br><br>'
        
        return result_str
