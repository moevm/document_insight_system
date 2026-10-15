from unittest.mock import MagicMock

from app.main.checks.report_checks.decimal_places import ReportDecimalPlacesCheck
from tests.util.report_file_utils import create_report_file_info


class TestReportDecimalPlacesCheck:
    def _make_checker(self, reports_fixture_dir, fixture, text, max_violations=0, max_decimal_places=2):
        file_info = create_report_file_info(reports_fixture_dir / "decimal_places_check" / fixture)
        checker = ReportDecimalPlacesCheck(
            file_info, max_decimal_places=max_decimal_places, max_violations=max_violations
        )
        pages = text if isinstance(text, dict) else {1: text}
        file_info['file'].pdf_file.get_text_on_page = MagicMock(return_value=pages)
        return checker

    def _check(self, reports_fixture_dir, fixture, text, **params):
        return self._make_checker(reports_fixture_dir, fixture, text, **params).check()

    def test_01_valid_places(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "1.23")
        assert result["score"] == 1.0

    def test_02_too_many_places(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "1.2345")
        assert result["score"] == 0.0

    def test_03_ignore_ip_address(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "IP address 192.168.1.1 is here")
        assert result["score"] == 1.0

    def test_04_ignore_date(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Date 25.05.2023")
        assert result["score"] == 1.0

    def test_05_comma_separator(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Value with comma 1,2345")
        assert result["score"] == 0.0

    def test_06_ignore_gost(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Оформлено по ГОСТ 2.105-95")
        assert result["score"] == 1.0

    def test_07_ignore_gost_with_letter(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Согласно ГОСТ Р 2.105-95 и ГОСТ Р 7.0.100-2018")
        assert result["score"] == 1.0

    def test_08_ignore_gost_lowercase(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "по гост 2.105-95")
        assert result["score"] == 1.0

    def test_09_number_after_gost_is_checked(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "ГОСТ 2.105-95, значение 1.2345")
        assert result["score"] == 0.0
        assert "<b>1.2345</b>" in result["verdict"][0]
        assert "<b>2.105</b>" not in result["verdict"][0]

    def test_10_ignore_url(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir, "valid.md", "Источник: https://site.ru/data/1.23456 и http://site.ru/3.14159"
        )
        assert result["score"] == 1.0

    def test_11_number_after_url_is_checked(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "https://site.ru/1.23456 и число 3.14159")
        assert result["score"] == 0.0
        assert "<b>3.14159</b>" in result["verdict"][0]

    def test_12_ignore_doi(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "DOI: 10.12345/abc, doi: 10.54321/xyz")
        assert result["score"] == 1.0

    def test_13_ignore_doi_org(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "см. doi.org/10.12345/abc")
        assert result["score"] == 1.0

    def test_14_violations_within_limit(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "1.2345 и 2.3456", max_violations=3)
        assert result["score"] == 1.0
        assert "Всего нарушений: 2" in result["verdict"][0]

    def test_15_violations_over_limit(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "1.2345 2.3456 3.4567 4.5678", max_violations=3)
        assert result["score"] == 0.0
        assert "Всего нарушений: 4" in result["verdict"][0]

    def test_16_exactly_max_places(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Значения 3,14 и 2.71")
        assert result["score"] == 1.0

    def test_17_one_over_max_places(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Значение 3,141")
        assert result["score"] == 0.0

    def test_18_custom_max_places(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Значение 1.2345", max_decimal_places=4)
        assert result["score"] == 1.0

    def test_19_integers_ignored(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "В 2024 году обработано 123456 записей")
        assert result["score"] == 1.0

    def test_20_ignore_dotted_chain(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Номер 123.123.123 и версия 1.2.3")
        assert result["score"] == 1.0

    def test_21_ignore_version(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Используется Python v3.12.15")
        assert result["score"] == 1.0

    def test_22_long_integer_part(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Скорость 1234.56789 м/с")
        assert result["score"] == 0.0
        assert "<b>1234.56789</b>" in result["verdict"][0]

    def test_23_long_integer_part_comma(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Масса 15000,123 кг")
        assert result["score"] == 0.0
        assert "<b>15000,123</b>" in result["verdict"][0]

    def test_24_negative_number(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Температура -1.2345 градусов")
        assert result["score"] == 0.0

    def test_25_number_at_end_of_sentence(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Точность равна 0.98765. Далее текст")
        assert result["score"] == 0.0
        assert "<b>0.98765</b>" in result["verdict"][0]

    def test_26_valid_number_at_end_of_sentence(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Точность равна 0.98. Далее текст")
        assert result["score"] == 1.0

    def test_27_number_with_unit(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Длина 1.2345мм")
        assert result["score"] == 0.0

    def test_28_comma_separated_list(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Значения: 1,2345, 2,3456", max_violations=5)
        assert "Всего нарушений: 2" in result["verdict"][0]

    def test_29_number_in_parentheses(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Ошибка (0.12345) мала")
        assert result["score"] == 0.0

    def test_30_line_number_in_verdict(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Первая строка 1.23\nВторая строка 4.5678")
        assert result["score"] == 0.0
        assert "Строка 2" in result["verdict"][0]
        assert "Строка 1" not in result["verdict"][0]

    def test_31_violations_on_several_pages(self, reports_fixture_dir):
        result = self._check(
            reports_fixture_dir, "invalid.md", {1: "Число 1.2345", 3: "Число 3.4567"}, max_violations=5
        )
        assert result["score"] == 1.0
        assert "Всего нарушений: 2" in result["verdict"][0]
        assert "#page=1" in result["verdict"][0]
        assert "#page=3" in result["verdict"][0]

    def test_32_empty_page(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "")
        assert result["score"] == 1.0
        assert "Проверка пройдена" in result["verdict"][0]

    def test_33_ignore_comma_chain(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "valid.md", "Население 1,234,567,135 человек")
        assert result["score"] == 1.0

    def test_34_comma_after_word_before_number(self, reports_fixture_dir):
        result = self._check(reports_fixture_dir, "invalid.md", "Значения,1.2345")
        assert result["score"] == 0.0
