import '../styles/upload.css';


let upload_id;
var pdf_uploaded = false;
var file_uploaded = false;
const file_input = $("#upload_file");
const pdf_file_input = $("#upload_file_pdf");
const upload_button = $("#upload_upload_button");

upload_button.prop("disabled", true);

pdf_file_input.change(() => {
    const fileName = pdf_file_input.val().split("\\")[2];
    let file = pdf_file_input.prop("files")[0];
    let label = $("#upload_file_label_pdf")
    let file_limit = file_upload_limit/1024/1024
    if (file.size > file_upload_limit) {
        label.html(`Формат: pptx (объем не больше ${file_upload_limit / 1024 / 1024} Мб.)`);
        alert(
        "Объем загружаемого вами документа " + (fileName) + " превышает максимально разрешенный объем " + (file_limit) + " МБ." +
        " Для уменьшения объема файла, мы рекомендуем следующие действия: \n" +
        "    ∙ общее — снизить разрешение изображений, \n    ∙ для презентаций — временно убрать дополнительные слайды.");
        return;
    }
    pdf_uploaded = true;
    label.html(fileName);
    if (file_uploaded === true) {
        upload_button.prop("disabled", false);
    }
});

file_input.change(() => {
    const fileName = file_input.val().split("\\")[2];
    let file = file_input.prop("files")[0];
    let label = $("#upload_file_label")
    let file_limit = file_upload_limit/1024/1024
    if (file.size > file_upload_limit) {
        label.html(`Формат: pptx (объем не больше ${file_upload_limit / 1024 / 1024} Мб.)`);
        alert(
        "Объем загружаемого вами документа " + (fileName) + " превышает максимально разрешенный объем " + (file_limit) + " МБ." +
        " Для уменьшения объема файла, мы рекомендуем следующие действия: \n" +
        "    ∙ общее — снизить разрешение изображений, \n    ∙ для презентаций — временно убрать дополнительные слайды.");
        return;
    }
    file_uploaded = true;
    label.html(fileName);
    upload_button.prop("disabled", false);
});

async function upload() {
    let file = file_input.prop("files")[0];
    let formData = new FormData();
    if (pdf_uploaded === true) {
        let pdf_file = pdf_file_input.prop("files")[0];
        formData.append("pdf_file", pdf_file);
    }
    formData.append("file", file);
    formData.append("file_type", file_type);
    if ($('div.g-recaptcha').length) {
        let response = grecaptcha.getResponse();
        formData.append("g-recaptcha-response", response);
    }

    const bar = $("#uploading_progress");
    $("#uploading_progress_holder").css("display", "block");
    if (file_input.hasClass("is-invalid")) file_input.removeClass("is-invalid");
    if (pdf_file_input.hasClass("is-invalid")) pdf_file_input.removeClass("is-invalid");
    if (bar.hasClass("bg-danger")) bar.removeClass("bg-danger");
    if (bar.hasClass("bg-success")) bar.removeClass("bg-success");

    const post_data = {
        method: "POST",
        body: formData
    };
    const response_text = await (await fetch("/upload", post_data)).text();
    console.log("Answer:", response_text);
    bar.css("width", "100%").attr('aria-valuenow', 100);
    console.log(file);
    if (response_text === 'storage_overload') {
        alert('Система перегружена, попробуйте повторить запрос позднее');
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
        pdf_file_input.addClass("is-invalid");
    } else if (response_text.includes('Not OK') || response_text === 'File exceeded the upload limit') {
        alert(response_text);
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
        pdf_file_input.addClass("is-invalid");
    } else {
        file_uploaded = false;
        pdf_uploaded = false;
        upload_id = JSON.parse(response_text)['check_id'];
        bar.addClass("bg-success");
        window.location.replace("/results/" + upload_id);
    }
}

upload_button.click(async () => {
    if ($('div.g-recaptcha').length && grecaptcha.getResponse().length === 0) {
        alert('Check recaptcha to continue!');
    } else {
        upload_button.prop("disabled", true);
        await upload();
    }
});