import altair as alt
import pandas as pd
import streamlit as st

import storage
from verdict import DEFAULT_THRESHOLDS, evaluate, outcome

st.set_page_config(page_title="Анализ изображений на проекторе", layout="wide")

LABELS = {"terrible": "ужасно", "meh": "так себе", "ok": "нормально"}
COLORS = {"ужасно": "#d13b3b", "так себе": "#d99a1e", "нормально": "#2e9b5a", "без разметки": "#9aa1ab"}

SLIDERS = [
    ("min_brightness", "Яркость", 0.0, 1.0, 0.01, "Средняя светлота картинки от 0 (чёрная) до 1 (белая)."),
    ("min_bg_brightness", "Яркость фона", 0.0, 1.0, 0.01, "Светлота фона. Ловит тёмные темы."),
    ("min_contrast", "Контраст", 1.0, 10.0, 0.1, "Контраст фона и содержимого по WCAG, от 1 до 21."),
    ("min_projected_contrast", "Контраст на проекторе", 1.0, 10.0, 0.1, "Тот же контраст с засветкой зала."),
    ("ambient_light", "Засветка зала", 0.0, 0.5, 0.01, "0.1 для зашторенного зала, 0.2 для пасмурного дня у окон."),
    ("min_bg_share", "Минимальная доля фона", 0.0, 1.0, 0.01,
     "Если фон меньше, контраст считается между тёмными и светлыми участками всей картинки."),
    ("dark_bg_below", "Порог тёмного фона", 0.0, 1.0, 0.01,
     "Фон темнее этого значения считается тёмным, и для него проверяется размер текста."),
    ("min_line_pitch_on_dark", "Шаг строк на тёмном фоне", 0.0, 0.1, 0.001,
     "Расстояние между строками текста в долях ширины картинки. Чем меньше, тем мельче текст на слайде."),
]


def save_label(name: str) -> None:
    storage.save_label(name, st.session_state[f"label::{name}"])


def reset_thresholds() -> None:
    for key, value in DEFAULT_THRESHOLDS.items():
        st.session_state[f"threshold::{key}"] = value


def sidebar() -> dict:
    if "threshold::min_brightness" not in st.session_state:
        reset_thresholds()
    with st.sidebar:
        st.header("Пороги")
        st.caption("Чтобы выключить метрику, сдвинь её порог влево до упора.")
        thresholds = {
            key: st.slider(title, low, high, step=step, help=hint, key=f"threshold::{key}")
            for key, title, low, high, step, hint in SLIDERS
        }
        st.button("Сбросить пороги", on_click=reset_thresholds)
        return thresholds


def build_items(thresholds: dict) -> list[dict]:
    labels = storage.load_labels()
    items = []
    for name, entry in storage.load_metrics().items():
        evaluation = evaluate(entry["metrics"], thresholds) if entry["metrics"] else None
        label = labels.get(name)
        items.append({
            "name": name,
            "error": entry["error"],
            "evaluation": evaluation,
            "bg_brightness": entry["metrics"]["bg_brightness"] if entry["metrics"] else None,
            "label": label,
            "outcome": outcome(label, evaluation.flagged) if evaluation else "error",
        })
    return items


def summary(items: list[dict]) -> None:
    def count(kind: str) -> int:
        return sum(item["outcome"] == kind for item in items)

    left, middle, right = st.columns(3)
    left.metric("«Ужасных» поймано", f"{count('tp')} / {count('tp') + count('fn')}")
    middle.metric("«Нормальных» задето зря", f"{count('fp')} / {count('fp') + count('tn')}")
    right.metric("Без разметки", sum(item["label"] is None for item in items))


def clear_selection() -> None:
    st.session_state["chart_version"] = st.session_state.get("chart_version", 0) + 1


def chart(items: list[dict], thresholds: dict) -> list[str]:
    rows = [
        {
            "картинка": item["name"],
            "яркость фона": item["bg_brightness"],
            "контраст на проекторе": item["evaluation"].projected_contrast,
            "разметка": LABELS.get(item["label"], "без разметки"),
            "ошибка модели": item["outcome"] in ("fn", "fp"),
        }
        for item in items
        if item["evaluation"] and item["evaluation"].has_background and item["evaluation"].projected_contrast
    ]
    if not rows:
        return []
    pick = alt.selection_point(name="pick", fields=["картинка"])
    points = alt.Chart(pd.DataFrame(rows)).mark_circle(size=150).encode(
        opacity=alt.condition(pick, alt.value(0.95), alt.value(0.25)),
        x=alt.X("яркость фона:Q", scale=alt.Scale(domain=[0, 1])),
        y=alt.Y("контраст на проекторе:Q", scale=alt.Scale(type="log", domain=[1, 21])),
        color=alt.Color("разметка:N", scale=alt.Scale(domain=list(COLORS), range=list(COLORS.values()))),
        stroke=alt.condition("datum['ошибка модели']", alt.value("black"), alt.value("white")),
        strokeWidth=alt.condition("datum['ошибка модели']", alt.value(3), alt.value(1)),
        tooltip=["картинка", alt.Tooltip("яркость фона:Q", format=".2f"),
                 alt.Tooltip("контраст на проекторе:Q", format=".2f")],
    ).add_params(pick)
    rule_x = alt.Chart(pd.DataFrame({"x": [thresholds["min_bg_brightness"]]})).mark_rule(strokeDash=[5, 4]).encode(x="x:Q")
    rule_y = alt.Chart(pd.DataFrame({"y": [thresholds["min_projected_contrast"]]})).mark_rule(strokeDash=[5, 4]).encode(y="y:Q")
    event = st.altair_chart(points + rule_x + rule_y, width="stretch", on_select="rerun",
                            key=f"chart::{st.session_state.get('chart_version', 0)}")
    st.caption("Пунктиром показаны пороги, чёрной обводкой ошибки модели. Клик по точке показывает картинку под графиком. "
               "Картинки без явного фона на графике не показаны.")
    return [point["картинка"] for point in event["selection"].get("pick", [])]


def number(value: float) -> str:
    return f"{value:.3f}" if abs(value) < 0.1 else f"{value:.2f}"


def clickable_image(column, url: str, caption: str) -> None:
    column.markdown(
        f'<a href="{url}" target="_blank" title="Открыть в полном размере">'
        f'<img src="{url}" style="width:100%;border-radius:4px"></a>'
        f'<div style="font-size:0.8rem;color:gray;text-align:center">{caption}</div>',
        unsafe_allow_html=True,
    )


def card(item: dict, ambient: float) -> None:
    evaluation = item["evaluation"]
    if evaluation is None:
        badge = ":gray-badge[не открылась]"
    elif evaluation.flagged:
        badge = ":red-badge[критерий сработал]"
    else:
        badge = ":green-badge[прошла]"
    if item["outcome"] == "fn":
        badge += " :orange-badge[пропущено]"
    if item["outcome"] == "fp":
        badge += " :orange-badge[зря]"
    st.markdown(f"**{item['name']}**  \n{badge}")

    if evaluation is None:
        st.error(item["error"])
    else:
        left, right = st.columns(2)
        clickable_image(left, storage.render(item["name"]), "оригинал")
        clickable_image(right, storage.render(item["name"], ambient), "на проекторе")
        rows = ["| | Метрика | Значение | Порог |", "|---|---|--:|--:|"]
        for check in evaluation.checks:
            if check.value is None:
                rows.append(f"| | {check.name} | нет | не применимо |")
            elif check.passed:
                rows.append(f"| ✓ | {check.name} | {number(check.value)} | ≥ {number(check.limit)} |")
            else:
                rows.append(f"| :red[✗] | :red[**{check.name}**] | :red[**{number(check.value)}**] | :red[≥ {number(check.limit)}] |")
        st.markdown("\n".join(rows))

    key = f"label::{item['name']}"
    if key not in st.session_state:
        st.session_state[key] = item["label"]
    st.segmented_control("Разметка", list(LABELS), format_func=LABELS.get, key=key,
                         on_change=save_label, args=(item["name"],), label_visibility="collapsed")


def cards(items: list[dict], ambient: float, selected: list[str]) -> None:
    if selected:
        st.button("Показать все картинки", on_click=clear_selection)
        items = [item for item in items if item["name"] in selected]
        for column, item in zip(st.columns(3), items):
            with column, st.container(border=True):
                card(item, ambient)
        return
    show = st.radio("Показать", ["все", "ошибки модели", "без разметки", *LABELS.values()], horizontal=True)
    if show == "ошибки модели":
        items = [item for item in items if item["outcome"] in ("fn", "fp")]
    elif show == "без разметки":
        items = [item for item in items if item["label"] is None]
    elif show != "все":
        items = [item for item in items if LABELS.get(item["label"]) == show]
    st.caption(f"Показано: {len(items)}")
    for start in range(0, len(items), 3):
        for column, item in zip(st.columns(3), items[start:start + 3]):
            with column, st.container(border=True):
                card(item, ambient)


def main() -> None:
    st.title("Анализ изображений на проекторе")
    thresholds = sidebar()
    with st.spinner("Считаю метрики..."):
        items = build_items(thresholds)
    if not items:
        st.info(f"Положи картинки в папку {storage.IMAGES_DIR}")
        return
    summary(items)
    selected = chart(items, thresholds)
    cards(items, thresholds["ambient_light"], selected)


main()
