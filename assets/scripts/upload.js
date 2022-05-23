import '../styles/upload.css';


let upload_id;
const file_input = $("#upload_file");
const upload_button = $("#upload_upload_button");
const document_type_select = $("#document_type");
const textfiles_extensions = ['doc', 'docx', "odt"];

upload_button.prop("disabled", true);
document_type_select.prop("hidden", true);

file_input.change(() => {
    const fileName = file_input.val().split("\\")[2];
    let file = file_input.prop("files")[0];
    if (file.size > file_upload_limit){
      $("#upload_file_label").html(`Exceeded the ${file_upload_limit/1024/1024} MB file limit.`);
      return;
    }
    $("#upload_file_label").html(fileName);
    upload_button.prop("disabled", false);
    if (textfiles_extensions.includes(fileName.split('.').pop())){
        document_type_select.prop("hidden", false);
    }else{
        document_type_select.prop("hidden", true);
    }
});

async function upload(sample = false) {
    let presentation = file_input.prop("files")[0];
    let formData = new FormData();
    formData.append("presentation", presentation);
    if ($('div.g-recaptcha').length){
        let response = grecaptcha.getResponse();
        formData.append("g-recaptcha-response", response);};

    const bar = $("#uploading_progress");
    $("#uploading_progress_holder").css("display", "block");
    if (file_input.hasClass("is-invalid")) file_input.removeClass("is-invalid");
    if (bar.hasClass("bg-danger")) bar.removeClass("bg-danger");
    if (bar.hasClass("bg-success")) bar.removeClass("bg-success");

    const post_data = { method: "POST" };
    if (!sample) post_data.body = formData;
    const response_text = await (await fetch("/upload", post_data)).text();
    console.log("Answer:", response_text);
    bar.css("width", "100%").attr('aria-valuenow', 100);
    console.log(presentation);
    if (response_text == 'storage_overload') {
        alert('Система перегружена, попробуйте повторить запрос позднее');
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
    } else if (response_text.includes('Not OK') || response_text == 'File exceeded the upload limit') {
        alert(response_text);
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
    } else if (textfiles_extensions.includes(presentation.name.split('.').pop())) {
        console.log(presentation.name)
        upload_id = response_text;
      bar.addClass("bg-success");
      window.location.replace("/parse_results/" + upload_id);
    } else {
      upload_id = response_text;
      bar.addClass("bg-success");
      window.location.replace("/results/" + upload_id);
    }
}

$("#upload_upload_button").click(async () =>{
     if ($('div.g-recaptcha').length && grecaptcha.getResponse().length === 0){
          alert('Check recaptcha to continue!');
        }
        else{
          upload_button.prop("disabled", true);
          await upload(false);
    }});
