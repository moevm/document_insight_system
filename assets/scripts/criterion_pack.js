const pack_form = $("#pack_form")
const file_type = $("#file_type")

$('.alert').hide()

const RAW_CRITERION_VALIDATION_ERRORS = {
    'not_json': 'Строка не является JSON-строкой',
}

$("#file_type").change(function () {
    switch ($(this).val()) {
        case "pres": {
            $("#report_type").attr('disabled', true)
            $("#report_type").attr('hidden', true)
            break;
        }
        case "report": {
            $("#report_type").attr('disabled', false)
            $("#report_type").attr('hidden', false)
            break;
        }
    }
})

pack_form.submit((e) => {
    e.preventDefault();
    $('.alert').hide()
    let raw_criterions_str = $("#raw_criterions").val();
    switch (verifyRawCriterions(raw_criterions_str)) {
        case 0: {
            console.log('ok')
            break;
        }
        case 1: {
            $("#alert").show();
            $("#error-text").text("Список критериев должен быть JSON-строкой")
            return;
        }
    }
    let fd = new FormData();
    fd.append('pack_name', $("#pack_name").val());
    fd.append('file_type', $("#file_type").val());
    fd.append('report_type', $("#report_type").val());
    fd.append('min_score', $("#min_score").val());
    fd.append('raw_criterions', raw_criterions_str);
    fetch(`/api/criterion_pack`, {method: "POST", body: fd})
        .then(response => {
            if (response.status === 200) {
                response.json().then(responseJson => {
                    $("#alert-success").show()
                    $("#success-text").text(`${responseJson['data']}\n${new Date(responseJson['time']).toString()}`)
                })
            } else {
                response.json().then(responseJson => {
                    $("#alert").show();
                    $("#error-text").text(`${responseJson['data']}\n${new Date(responseJson['time']).toString()}}`)
                })
            }
        })
        .catch((err) => {
            console.log(`Fetch /api/criterion_pack error:`, err);
            $("#alert").show();
            $("#error-text").text(err)
        });
})

function verifyRawCriterions(text) {
    try {
        JSON.parse(text);
        return 0;
    } catch (e) {
        console.log(text, e)
        return 1;
    }
}