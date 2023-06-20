import '../styles/upload.css';

let upload_id;
var pdf_uploaded = false;
var file_uploaded = false;
const file_input = $("#upload_file");
const file_label = $("#upload_file_label");
const return_file_label = file_label.text();

const pdf_file_input = $("#upload_file_pdf");
const pdf_file_label = $("#upload_file_label_pdf");
const return_pdf_file_label = pdf_file_label.text();

const upload_button = $("#upload_upload_button");
upload_button.prop("disabled", true);

const showMessage = () => {
  alert(
        "Объем загружаемых вами файлов превышает максимально разрешенный объем " + (file_upload_limit/1024/1024) + " МБ." +
        " Для уменьшения объема файла, мы рекомендуем следующие действия: \n" +
        "    ∙ общее — снизить разрешение изображений, \n    ∙ для презентаций — временно убрать дополнительные слайды.");
};

const resetFileUpload = () => {
  pdf_file_input.val('');
  pdf_file_label.html(return_pdf_file_label);
  file_input.val('');
  file_label.html(return_file_label);
  pdf_uploaded = false;
  file_uploaded = false;
  upload_button.prop("disabled", true);
};

const changeUploadButton = () => {
  if (pdf_uploaded || file_uploaded) {
    const pdf_size = pdf_file_input.prop("files")[0]?.size || 0;
    const file_size = file_input.prop("files")[0]?.size || 0;
    if (pdf_size + file_size <= file_upload_limit) {
      upload_button.prop("disabled", false);
    } else {
      showMessage();
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
  if (file && file.size > file_upload_limit) {
    showMessage();
    resetFileUpload();
    return;
  }
  file_uploaded = true;
  pdf_uploaded = true;
  label.html(fileName);

  if (label.attr("id") === "upload_file_label_pdf") {
    pdf_uploaded = !!file;
    pdf_file_label.html(file ? fileName : original_pdf_file_label);
  } else {
    file_uploaded = !!file;
    file_label.html(file ? fileName : original_file_label);
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
        alert('База данных перегружена (недостаточно места для загрузки новых файлов). Свяжитесь с администратором');
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
