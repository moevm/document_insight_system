import '../styles/criteria.css';

const goals_slide = $("#goals_slide");

const every_task_percent = $("#every_task_percent");
const slide_every_task = $("#slide_every_task");
const actuality_percent = $("#actuality_percent");
const conclusions = $("#conclusion_actual, #conclusion_along");

const criteria_save_button = $("#criteria_save_button");


$("input").change(function () {
    switch (this.id) {
        case "slides_number":
            const checked = $(this).prop("checked");
            if (checked) $("#bachelors").prop("checked", true);
            $("#slides_number_options_holder .form-check-input").prop("disabled", !checked);
            break;
        case "slide_every_task":
            every_task_percent.prop("disabled", !$(this).prop("checked"));
            break;
        case "conclusion_actual":
            actuality_percent.prop("disabled", !$(this).prop("checked"));
            break;
        case "every_task_percent":
            $("#every_task_percent_label").text("Процент точности поиска: " + $(this).val() + "%");
            break;
        case "actuality_percent":
            $("#actuality_percent_label").text("Процент соответствия результатов целям: " + $(this).val() + "%");
            break;
        case "goals_slide":
            const goals_available = goals_slide.prop("checked");
            if (!goals_available) {
                slide_every_task.prop("checked", false);
                every_task_percent.prop("disabled", true);
            }
            slide_every_task.prop("disabled", !goals_available);
        case "conclusion_slide":
            const conclusion_goals_available = $("#goals_slide").prop("checked") && $("#conclusion_slide").prop("checked");
            if (!conclusion_goals_available) {
                conclusions.prop("checked", false);
                actuality_percent.prop("disabled", true);
            }
            conclusions.prop("disabled", !conclusion_goals_available);
            break;
    }
});



function save_button_popover (text) {
    return {
        placement: "auto",
        trigger: "manual",
        content: text
    };
}

criteria_save_button.click(async function () {
    const necessary_fields = $("input[type=checkbox]");
    const criteria = Object();
    for (const field of necessary_fields) criteria[field.id] = $(field).prop("checked") ? 0 : -1;

    if (Object.values(criteria).every(x => (x === -1))) $(this).popover(save_button_popover("Сохранена проверка без критериев!"));
    else $(this).popover(save_button_popover("Проверка сохранена!"));
    $(this).popover("show");
    setTimeout(() => { $(this).popover("dispose"); }, 1000);

    if (criteria.slides_number !== -1) {
        if ($("#bachelors").prop("checked")) criteria.slides_number = 12;
        else if ($("#masters").prop("checked")) criteria.slides_number = 15;
    }
    if (criteria.slide_every_task === 0) criteria.slide_every_task = Number.parseInt(every_task_percent.val());
    if (criteria.conclusion_actual === 0) criteria.conclusion_actual = Number.parseInt(actuality_percent.val());

    const post_data = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(criteria)
    };
    await fetch("/criteria", post_data);
});
