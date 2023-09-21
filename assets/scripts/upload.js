import '../styles/upload.css';

let upload_id;
let pdf_uploaded = false;
let file_uploaded = false;
const file_input = $("#upload_file");
const file_label = $("#upload_file_label");
const return_file_label = file_label.text();

const pdf_file_input = $("#upload_file_pdf");
const pdf_file_label = $("#upload_file_label_pdf");
const return_pdf_file_label = pdf_file_label.text();

const upload_button = $("#upload_upload_button");
upload_button.prop("disabled", true);

// Для проверки расширения файла.
let file_ext_re = /(?:\.([^.]+))?$/;
let file_formats = $("#upload_file_label").text().split(":");
file_formats = file_formats[file_formats.length - 1];
file_formats = file_formats.replaceAll(" ", "");
file_formats = file_formats.split(",");

const showSizeExceedMessage = () => {
    alert(
        "Объем загружаемых вами файлов превышает максимально разрешенный объем " + (file_upload_limit / 1024 / 1024) + " МБ." +
        " Для уменьшения объема файла, мы рекомендуем следующие действия: \n" +
        "    ∙ общее — снизить разрешение изображений, \n    ∙ для презентаций — временно убрать дополнительные слайды.");
};

const showWrongExtensionMessage = () => {
    alert("Был загружен файл неправильного расширения.")
};

const showRealTypeMessage = () => {
    alert("Один из загруженных файлов имеет расширение не соответствующее реальному типу файлу.")
};

const showBdOverwhelmedMessage = () => {
    alert('База данных перегружена (недостаточно места для загрузки новых файлов). Свяжитесь с администратором');
}

const showRecaptchaMessage = () => {
    alert('Пройдите recaptcha, чтобы продолжить!');
}

const resetFileUpload = () => {
    pdf_uploaded = false;
    pdf_file_input.val('');
    pdf_file_label.html(return_pdf_file_label);

    file_uploaded = false;
    file_input.val('');
    file_label.html(return_file_label);

    upload_button.prop("disabled", true);
};

const changeUploadButton = () => {
    if (pdf_uploaded || file_uploaded) {
        const pdf_size = pdf_file_input.prop("files")[0]?.size || 0;
        const file_size = file_input.prop("files")[0]?.size || 0;
        if (pdf_size + file_size <= file_upload_limit) {
            if (file_uploaded)
                upload_button.prop("disabled", false);
        } else {
            showSizeExceedMessage();
            resetFileUpload();
            upload_button.prop("disabled", true);
        }
    } else {
        upload_button.prop("disabled", true);
    }
};

const selectFileUpload = (input, label) => {
    const fileName = input.val().split("\\")[2];
    const file = input.prop("files")[0];

    // Проверка на валидность загруженного файла.
    if (file && file.size > file_upload_limit) {
        showSizeExceedMessage();
        resetFileUpload();
        return;
    } else if (file) {
        if (label.attr("id") === "upload_file_label_pdf") {
            // Загружен pdf.
            if (file_ext_re.exec(fileName)[1] !== 'pdf') {
                showWrongExtensionMessage();
                resetFileUpload();
                return;
            }
        } else {
            // Загружен основной документ.
            if (! file_formats.includes(file_ext_re.exec(fileName)[1])) {
                showWrongExtensionMessage();
                resetFileUpload();
                return;
            }
        }
    }

    // Если все верно загружено.
    if (label.attr("id") === "upload_file_label_pdf") {
        pdf_uploaded = !!file;
        label.html(file ? fileName : return_pdf_file_label);
    } else {
        file_uploaded = !!file;
        label.html(file ? fileName : return_file_label);
    }
    changeUploadButton();
}

pdf_file_input.change(() => selectFileUpload(pdf_file_input, pdf_file_label));
file_input.change(() => selectFileUpload(file_input, file_label));

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
        showBdOverwhelmedMessage();
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
        pdf_file_input.addClass("is-invalid");
    } else if (response_text.includes('Not OK') || response_text === 'File exceeded the upload limit') {
        showSizeExceedMessage();
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
        pdf_file_input.addClass("is-invalid");
    } else if (response_text === 'not_allowed_extension') {
        showWrongExtensionMessage();
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
        resetFileUpload();
    } else if (response_text === 'pdf_not_allowed_extension') {
        showWrongExtensionMessage();
        bar.addClass("bg-danger");
        pdf_file_input.addClass("is-invalid");
        resetFileUpload();
    } else if (response_text === 'mime_type_does_not_match_extension') {
        showRealTypeMessage();
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
        resetFileUpload();
    } else if (response_text === 'pdf_mime_type_does_not_match_extension') {
        showRealTypeMessage();
        bar.addClass("bg-danger");
        pdf_file_input.addClass("is-invalid");
        resetFileUpload();
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
        showRecaptchaMessage();
    } else {
        upload_button.prop("disabled", true);
        await upload();
    }
});