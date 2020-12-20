import '../styles/criteria.css';


const actuality_percent = $("#actuality_percent");
const conclusion_actual = $("#conclusion_actual");


$("input").change(function () {
    switch (this.id) {
        case "conclusion_actual":
            actuality_percent.prop("disabled", !$(this).prop("checked"));
            break;
        case "actuality_percent":
            $("#actuality_percent_label").text("Процент соответствия результатов целям: " + $(this).val() + "%");
            break;
        case "goals_slide":
        case "conclusion_slide":
            const conclusion_actual_available = $("#goals_slide").prop("checked") && $("#conclusion_slide").prop("checked");
            if (!conclusion_actual_available) {
                conclusion_actual.prop("checked", false);
                actuality_percent.prop("disabled", true);
            }
            conclusion_actual.prop("disabled", !conclusion_actual_available);
            break;
    }
});



$("#criteria_save_button").click(async () => {
    const fields = ["slides_number", "slides_enum", "slides_headers", "goals_slide", "probe_slide", "conclusion_slide", "actual_slide", "conclusion_actual"];
    const necessary_fields = $(fields.map(el => "#" + el).join(", ")); // в идеале, когда будут готовы все проверки, будет: $("input[type=checkbox]")

    const criteria = Object();
    for (const field of necessary_fields) criteria[field.id] = $(field).prop("checked") ? "" : -1;
    if (criteria.conclusion_actual === "") criteria.conclusion_actual = 0;
    criteria.actuality_percent = Number.parseInt(actuality_percent.val());

    const post_data = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(criteria)
    };
    await fetch("/criteria", post_data);
});
