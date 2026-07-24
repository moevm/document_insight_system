import re
from collections import defaultdict


class DecimalPlacesCheck:
    DECIMAL_PATTERN = r'\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\b'

    def __init__(self, file_info, max_decimal_places=2, max_violations=3):
        self.file_type = file_info['file_type']['type']
        self.max_decimal_places = max_decimal_places
        self.max_violations = max_violations

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

            for number_str, decimal_places, _ in line_violations:
                violations.append((line_idx, number_str, decimal_places, line))

        return violations

    def find_violations_in_texts(self, texts):
        pages = defaultdict(list)
        total_violations = 0

        for idx, text in texts:
            lines = re.split(r'\n', text)
            violations = self.find_violations_in_lines(lines)

            for line_idx, number_str, decimal_places, line in violations:
                total_violations += 1
                violation_msg = self.format_violation_message(line_idx, line, number_str, decimal_places)
                pages[idx].append(violation_msg)

        return (total_violations, pages)

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
        return (
            f'Проверка пройдена! Все числа имеют допустимое количество '
            f'десятичных знаков (не более {self.max_decimal_places}).'
        )

    def format_failure_message(self, total_violations, violations_by_location, format_page_link_fn=None):
        result_str = (
            f'<b>Найдены числа с избыточным количеством десятичных знаков!</b><br>'
            f'Максимально допустимое количество знаков после запятой: {self.max_decimal_places}<br>'
            f'Максимально допустимое количество нарушений: {self.max_violations}<br>'
            f'Всего нарушений: {total_violations}<br><br>'
        )

        for location_num, violations in violations_by_location.items():
            if format_page_link_fn:
                location_str = f'Страница {format_page_link_fn([location_num])}'
            else:
                location_str = f'Страница №{location_num}'

            result_str += f'<b>{location_str}:</b><br>'
            result_str += '<br>'.join(violations)
            result_str += '<br><br>'

        return result_str

    def get_result_msg_and_score(self, total_violations, detected_pages, format_page_link_fn=None):
        if total_violations > self.max_violations:
            result_str = self.format_failure_message(total_violations, detected_pages, format_page_link_fn)
            result_score = 0
        elif total_violations > 0:
            result_str = self.format_failure_message(total_violations, detected_pages, format_page_link_fn)
            result_score = 1.0
        else:
            result_str = self.format_success_message()
            result_score = 1.0
        return result_str, result_score
