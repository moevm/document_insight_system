import '../styles/upload.css';

let upload_id;
const file_input = $("#upload_file");
const fullname_input = $("#upload_fullname");
const group_input = $("#upload_group");
const comments_input = $("#upload_comments");
var need_data = {};
var got_data = {};
const upload_button = $("#upload_upload_button");

upload_button.prop("disabled", true);

function all_uploaded() {
    console.log("all?")
    if ("file" in need_data) {
        for (let i in need_data) {
            if ((need_data[i] === 1) && (i in got_data)){
                console.log(i, i)
            }
            else if (need_data[i] === 0) {console.log(i)}
            else {
                console.log(i, i, i)
                return false
            }
        }
        return true
    }
    return false
}

file_input.change(() => {
    need_data = optional
    console.log(need_data["comments"])
    need_data["file"] = 1;
    console.log(need_data["file"])

    const fileName = file_input.val().split("\\")[2];
    let file = file_input.prop("files")[0];
    let label = $("#upload_file_label")
    if (file.size > file_upload_limit) {
        label.html(`Exceeded the ${file_upload_limit / 1024 / 1024} MB file limit.`);
        return;
    }
    got_data["file"] = 1;
    label.html(fileName);
    if (all_uploaded() === true) {
        upload_button.prop("disabled", false);
    }
});

fullname_input.change(() => {
    got_data["fullname"] = 1;
    if (all_uploaded() === true) {
        upload_button.prop("disabled", false);
    }
});

group_input.change(() => {
    got_data["group"] = 1;
    if (all_uploaded() === true) {
        upload_button.prop("disabled", false);
    }
});

comments_input.change(() => {
    got_data["comments"] = 1;
    if (all_uploaded() === true) {
        upload_button.prop("disabled", false);
    }
});

async function upload() {
    let file = file_input.prop("files")[0];
    let formData = new FormData();
    formData.append("file", file);
    formData.append("file_type", file_type);
    for (let i in got_data) {
        if (i !== "file") {
        console.log(typeof(i))
            formData.append(i, document.getElementById("upload_" + i).value);
        }
    }
    if ($('div.g-recaptcha').length) {
        let response = grecaptcha.getResponse();
        formData.append("g-recaptcha-response", response);
    }

    const bar = $("#uploading_progress");
    $("#uploading_progress_holder").css("display", "block");
    if (file_input.hasClass("is-invalid")) file_input.removeClass("is-invalid");
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
    } else if (response_text.includes('Not OK') || response_text === 'File exceeded the upload limit') {
        alert(response_text);
        bar.addClass("bg-danger");
        file_input.addClass("is-invalid");
    } else {
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
