from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from PIL import Image

RGB = tuple[int, int, int]
FloatArray = NDArray[np.floating]


def srgb_to_linear(signal: float | FloatArray) -> FloatArray:
    return np.where(signal < 0.04045, signal / 12.92, ((signal + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(light: float | FloatArray) -> FloatArray:
    return np.where(
        light <= 0.0031308, light * 12.92, light ** (1.0 / 2.4) * 1.055 - 0.055
    )


LUMINANCE_WEIGHTS = np.array([0.2126, 0.7152, 0.0722])


def image_luminance(signal: FloatArray) -> FloatArray:
    return srgb_to_linear(signal) @ LUMINANCE_WEIGHTS


def relative_luminance(rgb: RGB) -> float:
    return float(image_luminance(np.array(rgb) / 255))


def lightness(y: float | FloatArray) -> FloatArray:
    def f(t):
        return np.where(t > 0.008856, t ** (1 / 3), 7.787 * t + (4 / 29))

    return (116 * f(y) - 16) / 100


def brightness(signal: FloatArray) -> float:
    return float(lightness(image_luminance(signal)).mean())


def wcag_contrast(y1: float, y2: float, ambient: float = 0.0) -> float:
    max_brightness = max(y1, y2)
    min_brightness = min(y1, y2)
    return (max_brightness + ambient + 0.05) / (min_brightness + ambient + 0.05)


def find_background(signal: FloatArray, bins: int = 64) -> tuple[FloatArray, float]:
    lightness_map = np.clip(lightness(image_luminance(signal)), 0, 1)
    bin_index = np.minimum((lightness_map * bins).astype(int), bins - 1)
    background_bin = np.bincount(bin_index.ravel(), minlength=bins).argmax()
    background_mask = bin_index == background_bin
    bg_rgb = np.median(signal[background_mask], axis=0)
    return bg_rgb, float(background_mask.mean())


def find_content(
    signal: FloatArray,
    bg_rgb: FloatArray,
    fg_delta: float = 0.1,
    fg_percentile: float = 50,
    min_fg_share: float = 0.001,
) -> tuple[FloatArray | None, float]:
    lightness_map = lightness(image_luminance(signal))
    bg_lightness = lightness(image_luminance(bg_rgb))
    distance = np.abs(lightness_map - bg_lightness)
    content_mask = distance > fg_delta
    fg_share = float(content_mask.mean())
    if not content_mask.any() or fg_share < min_fg_share:
        return None, fg_share
    threshold = np.percentile(distance[content_mask], fg_percentile)
    strong_mask = content_mask & (distance >= threshold)
    fg_rgb = np.median(signal[strong_mask], axis=0)
    return fg_rgb, fg_share


def content_profile(signal: FloatArray, bg_rgb: FloatArray, fg_delta: float = 0.1) -> FloatArray:
    distance = np.abs(lightness(image_luminance(signal)) - lightness(image_luminance(bg_rgb)))
    return (distance > fg_delta).mean(axis=1)


def pitch_by_autocorrelation(profile: FloatArray, min_strength: float = 0.3) -> int | None:
    centered = profile - profile.mean()
    if not centered.any():
        return None
    correlation = np.correlate(centered, centered, mode="full")[len(centered) - 1:]
    correlation = correlation / correlation[0]
    for lag in range(4, max(5, len(centered) // 3)):
        if correlation[lag] > correlation[lag - 1] and correlation[lag] >= correlation[lag + 1]:
            return lag if correlation[lag] >= min_strength else None
    return None


def pitch_by_runs(profile: FloatArray, min_run: int = 3) -> float | None:
    rows = np.concatenate([[False], profile > 0.002, [False]])
    edges = np.flatnonzero(np.diff(rows.astype(int)))
    starts, ends = edges[::2], edges[1::2]
    starts = starts[(ends - starts) >= min_run]
    if len(starts) < 2:
        return None
    return float(np.median(np.diff(starts)))


def line_pitch(signal: FloatArray, bg_rgb: FloatArray, fg_delta: float = 0.1) -> float | None:
    profile = content_profile(signal, bg_rgb, fg_delta)
    pitch = pitch_by_autocorrelation(profile) or pitch_by_runs(profile)
    return None if pitch is None else pitch / signal.shape[1]


def project_signal(signal: FloatArray, ambient: float) -> FloatArray:
    return linear_to_srgb((srgb_to_linear(signal) + ambient) / (1 + ambient))


def load_image(path: str | Path, max_side: int = 1024) -> FloatArray:
    with Image.open(path) as img:
        img = img.convert("RGBA")
    white_img_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(white_img_bg, img)
    img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    return np.asarray(img, dtype=np.float32) / 255


def analyze_image(
    path: str | Path,
    max_side: int = 1024,
    fg_delta: float = 0.1,
    fg_percentile: float = 75,
    min_fg_share: float = 0.001,
    global_percentiles: tuple[float, float] = (5, 95),
) -> dict:
    signal = load_image(path, max_side)
    bg_rgb, bg_share = find_background(signal)
    fg_rgb, fg_share = find_content(signal, bg_rgb, fg_delta, fg_percentile, min_fg_share)
    y_bg = float(image_luminance(bg_rgb))
    y_fg = None if fg_rgb is None else float(image_luminance(fg_rgb))
    y_low, y_high = (float(value) for value in np.percentile(image_luminance(signal), global_percentiles))
    return {
        "width": int(signal.shape[1]),
        "height": int(signal.shape[0]),
        "brightness": brightness(signal),
        "bg_rgb": bg_rgb.tolist(),
        "bg_share": bg_share,
        "bg_brightness": float(lightness(y_bg)),
        "y_bg": y_bg,
        "fg_rgb": None if fg_rgb is None else fg_rgb.tolist(),
        "fg_share": fg_share,
        "y_fg": y_fg,
        "contrast": None if y_fg is None else wcag_contrast(y_bg, y_fg),
        "y_low": y_low,
        "y_high": y_high,
        "global_contrast": wcag_contrast(y_low, y_high),
        "line_pitch": line_pitch(signal, bg_rgb, fg_delta),
    }
