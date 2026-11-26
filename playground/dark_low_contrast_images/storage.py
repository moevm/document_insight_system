import json
from pathlib import Path
from urllib.parse import quote

import numpy as np
from PIL import Image

from metrics import analyze_image, load_image, project_signal

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
METRICS_PATH = BASE_DIR / "data" / "metrics.json"
LABELS_PATH = BASE_DIR / "data" / "labels.json"
RENDERS_DIR = BASE_DIR / "static" / "renders"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp", ".tif", ".tiff", ".emf", ".wmf", ".svg"}
FULL_SIZE = 4096
METRICS_VERSION = 3


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def list_images() -> list[str]:
    if not IMAGES_DIR.exists():
        return []
    return sorted(path.name for path in IMAGES_DIR.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)


def analyze(name: str, mtime: float) -> dict:
    try:
        return {"mtime": mtime, "version": METRICS_VERSION, "metrics": analyze_image(IMAGES_DIR / name), "error": None}
    except Exception as error:
        return {"mtime": mtime, "version": METRICS_VERSION, "metrics": None, "error": f"{type(error).__name__}: {error}"}


def load_metrics() -> dict[str, dict]:
    cache = read_json(METRICS_PATH)
    result = {}
    for name in list_images():
        mtime = (IMAGES_DIR / name).stat().st_mtime
        cached = cache.get(name)
        fresh = cached and cached["mtime"] == mtime and cached.get("version") == METRICS_VERSION
        result[name] = cached if fresh else analyze(name, mtime)
    if result != cache:
        write_json(METRICS_PATH, result)
    return result


def load_labels() -> dict[str, str]:
    return read_json(LABELS_PATH)


def save_label(name: str, label: str | None) -> None:
    labels = load_labels()
    if label is None:
        labels.pop(name, None)
    else:
        labels[name] = label
    write_json(LABELS_PATH, labels)


def render(name: str, ambient: float = 0.0) -> str:
    target = RENDERS_DIR / f"{name}__{ambient:.2f}.png"
    if not target.exists() or target.stat().st_mtime < (IMAGES_DIR / name).stat().st_mtime:
        signal = load_image(IMAGES_DIR / name, FULL_SIZE)
        if ambient > 0:
            signal = project_signal(signal, ambient)
        RENDERS_DIR.mkdir(parents=True, exist_ok=True)
        Image.fromarray((np.clip(signal, 0, 1) * 255).round().astype(np.uint8)).save(target, "PNG")
    return f"app/static/renders/{quote(target.name)}"
