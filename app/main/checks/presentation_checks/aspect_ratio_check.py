import math

from ..base_check import BasePresCriterion, answer


class Ratio:
    ASCPECT_RATIO_PRECISION = 2

    def __init__(self, width, height):
        self.width = width
        self.height = height
        if height == 0:
            self.value = 0
        else:
            self.value = round(width / height, self.ASCPECT_RATIO_PRECISION)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        gcd_value = math.gcd(self.width, self.height)
        if gcd_value == 0:
            return "0:0"
        simplified_width = self.width // gcd_value
        simplified_height = self.height // gcd_value
        return f"{simplified_width}:{simplified_height}"


class PresAspectRatioCheck(BasePresCriterion):
    label = "Проверка соотношения сторон слайда"
    id = "pres_aspect_ratio_check"

    def __init__(self, file_info, correct_ratios=("16:9", "4:3")):
        super().__init__(file_info)
        self.correct_ratios = set(
            Ratio(*map(int, x.split(":"))) for x in correct_ratios
        )

    def __is_correct_ratio(self, aspect_ratio: Ratio):
        return aspect_ratio in self.correct_ratios

    def __convert_size_to_pixels(self, size, dpi=96):
        return math.trunc(size.inches * dpi)

    def __get_correct_instruction(self, aspect_ratio):
        correct_ratios_str = ", ".join(map(str, self.correct_ratios))
        width = self.__convert_size_to_pixels(aspect_ratio.width)
        height = self.__convert_size_to_pixels(aspect_ratio.height)
        return (
            f"Соотношение сторон слайдов ({width}x{
                height
            }) не соответствует стандарту<br/>"
            "Рекомендации по исправлению:<br/>"
            f"Измените соотношение сторон презентации на одно из доступных ({
                correct_ratios_str
            })"
        )

    def check(self):
        width = self.file.prs.slide_width
        height = self.file.prs.slide_height

        aspect_ratio = Ratio(width, height)

        if self.__is_correct_ratio(aspect_ratio):
            return answer(
                True,
                f"Соотношение сторон слайдов ({aspect_ratio}) соответствует стандарту.",
            )

        return answer(False, self.__get_correct_instruction(aspect_ratio))
