let upload_id;
const file_input = $("#upload_file");
const checking_button = $("#checking_button");
const upload_button = $("#upload_upload_button");

checking_button.prop("disabled", true);
upload_button.prop("disabled", true);

file_input.change(() => {
    const fileName = file_input.val().split("\\")[2];
    $("#upload_file_label").html(fileName);
    upload_button.prop('disabled', false);
});

/*
    0% - 10% = 0 -> 1
    10% - 60% = 1 -> 2
    60% - 90% = 2 -> 3
 */
function upload(sample = false) {
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
    fetch("/upload", post_data)
        .then((response) => {
            return response.text();
        }).then((response_text) => {
            console.log("Final answer:", response_text);
            bar.css("width", "100%").attr('aria-valuenow', 100);
            if (response_text === "") {
                bar.addClass("bg-danger");
                file_input.addClass("is-invalid");
            } else {
                upload_id = response_text;
                bar.addClass("bg-success");
                checking_button.prop("disabled", false);
            }
        });
}

function criteria() {
    window.location.href = "/criteria";
}

function check() {
    window.location.href = "/results/" + upload_id;
}
