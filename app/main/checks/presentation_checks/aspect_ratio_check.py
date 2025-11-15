import math

from ..base_check import BasePresCriterion, answer

class Ratio:
    ASPECT_RATIO_EPSILON = 0.01

    def __init__(self, width, height):
        self.width = width
        self.height = height
        if height == 0:
            self.value = 0
        else:
            self.value = width / height

    def __eq__(self, other):
        return math.isclose(self.value, other.value, rel_tol=self.ASPECT_RATIO_EPSILON)

    def __str__(self):
        gcd_value = math.gcd(self.width, self.height)
        if gcd_value == 0:
            return "0:0"
        simplified_width = self.width // gcd_value
        simplified_height = self.height // gcd_value
        return f'{simplified_width}:{simplified_height}'


class PresAspectRatioCheck(BasePresCriterion):
    label = "Проверка соотношения сторон слайда"
    description = ""
    id = 'pres_aspect_ratio_check'

    def __init__(self, file_info, correct_ratios=["4:3", "16:9"]):
        super().__init__(file_info)
        self.correct_ratios = [Ratio(*map(int, x.split(':'))) for x in correct_ratios]

    def __is_correct_ratio(self, aspect_ratio: Ratio):
        return any(aspect_ratio == ratio for ratio in self.correct_ratios)

    def check(self):
        width = self.file.prs.slide_width
        height = self.file.prs.slide_height

        aspect_ratio = Ratio(width, height)

        if self.__is_correct_ratio(aspect_ratio):
            return answer(True, f"Соотношение сторон слайдов ({aspect_ratio}) соответствует стандарту.")

        correct_ratios_str = ", ".join(map(str, self.correct_ratios))
        return answer(False,
                        f'Соотношение сторон слайдов ({aspect_ratio}) не соответствует стандарту ({correct_ratios_str}).')