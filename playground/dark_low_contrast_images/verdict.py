from dataclasses import dataclass

from metrics import wcag_contrast

DEFAULT_THRESHOLDS = {
    "min_brightness": 0.0,
    "min_bg_brightness": 0.0,
    "min_contrast": 3.0,
    "min_projected_contrast": 2.5,
    "ambient_light": 0.1,
    "min_bg_share": 0.4,
    "dark_bg_below": 0.25,
    "min_line_pitch_on_dark": 0.03,
}


@dataclass
class Check:
    name: str
    value: float | None
    limit: float

    @property
    def passed(self) -> bool:
        return self.value is None or self.value >= self.limit


@dataclass
class Evaluation:
    has_background: bool
    projected_contrast: float | None
    checks: list[Check]

    @property
    def flagged(self) -> bool:
        return any(not check.passed for check in self.checks)


def evaluate(metrics: dict, thresholds: dict) -> Evaluation:
    has_background = metrics["bg_share"] >= thresholds["min_bg_share"]
    if has_background:
        pair = None if metrics["y_fg"] is None else (metrics["y_bg"], metrics["y_fg"])
    else:
        pair = (metrics["y_low"], metrics["y_high"])
    contrast = None if pair is None else wcag_contrast(*pair)
    projected = None if pair is None else wcag_contrast(*pair, ambient=thresholds["ambient_light"])
    checks = [
        Check("Яркость", metrics["brightness"], thresholds["min_brightness"]),
        Check("Яркость фона", metrics["bg_brightness"] if has_background else None, thresholds["min_bg_brightness"]),
        Check(
            "Контраст фон/содержимое" if has_background else "Общий контраст (p5-p95)",
            contrast,
            thresholds["min_contrast"],
        ),
        Check("Контраст на проекторе", projected, thresholds["min_projected_contrast"]),
        Check(
            "Шаг строк на тёмном фоне",
            metrics.get("line_pitch") if has_background and metrics["bg_brightness"] < thresholds["dark_bg_below"] else None,
            thresholds["min_line_pitch_on_dark"],
        ),
    ]
    return Evaluation(has_background, projected, checks)


def outcome(label: str | None, flagged: bool) -> str:
    if label == "terrible":
        return "tp" if flagged else "fn"
    if label == "ok":
        return "fp" if flagged else "tn"
    return "none"
