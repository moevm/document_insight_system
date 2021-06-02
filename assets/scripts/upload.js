import '../styles/upload.css';


let upload_id;
const file_input = $("#upload_file");
const checking_button = $("#checking_button");
const upload_button = $("#upload_upload_button");

checking_button.prop("disabled", true);
upload_button.prop("disabled", true);

file_input.change(() => {
    const fileName = file_input.val().split("\\")[2];
    let file = file_input.prop("files")[0];
    if (file.size > file_upload_limit){
      $("#upload_file_label").html(`Exceeded the ${file_upload_limit/1024/1024} MB file limit.`);
      return;
    }
    $("#upload_file_label").html(fileName);
    upload_button.prop('disabled', false);
});

upload_button.click(async () => { await upload(false); });
$("#upload_test_button").click(async () => { await upload(true); });

async function upload(sample = false) {
    let presentation = file_input.prop("files")[0];
    let formData = new FormData();
    formData.append("presentation", presentation);

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
    if (response_text == 'storage_overload') {
        alert('Система перегружена, попробуйте повторить запрос позднее');
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
    } else if (response_text.includes('Not OK')) {
        alert(response_text);
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
    } else {
      upload_id = response_text;
      bar.addClass("bg-success");
      checking_button.prop("disabled", false);
    }
}

$("#upload_criteria_button").click(() => { window.location.href = "/criteria"; });
checking_button.click(() => { window.location.href = "/results/" + upload_id; });
