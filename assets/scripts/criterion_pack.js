const pack_form = $("#pack_form")

$('.alert').hide()

const RAW_CRITERION_VALIDATION_ERRORS = {
    'not_json': 'Строка не является JSON-строкой',
}

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
    fd.append('min_score', $("#min_score").val());
    fd.append('raw_criterions', raw_criterions_str);
    fetch(`/api${window.location.pathname}`, {method: "POST", body: fd})
        .then(response => {
            if (response.status === 200) {
                response.json().then(responseJson => {
                    $("#alert-success").show()
                    $("#success-text").text(`${responseJson['data']}<br>${responseJson['time']}`)
                })
            } else {
                response.json().then(responseJson => {
                    $("#alert").show();
                    $("#error-text").text(`${responseJson['data']}<br>${responseJson['time']}`)
                })
            }
        })
        .catch((err) => {
            console.log(`Fetch /api${window.location.pathname} error:`, err);
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