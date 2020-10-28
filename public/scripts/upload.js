let checking_presentation_uploading;

/*
    0% - 10% = 0 -> 1
    10% - 60% = 1 -> 2
    60% - 90% = 2 -> 3
 */
function upload(filename) {
    let presentation = $("#upload_file").prop("files")[0];
    let formData = new FormData();
    formData.append("presentation", presentation);

    let bar_size = 0;
    $("#uploading_progress_holder").css("display", "block");

    fetch("/upload", { method: "POST", body: formData })
        .then((response) => {
            clearInterval(checking_presentation_uploading);
            return response.text();
        }).then((response_text) => {
            console.log("Final answer:", response_text);
            const bar = $("#uploading_progress");
            bar.css("width", "100%").attr('aria-valuenow', 100);
            switch (response_text) {
                case "-1":
                    bar.addClass("bg-danger");
                    break;
                case "3":
                    bar.addClass("bg-success");
                    break;
            }
        });
    checking_presentation_uploading = setInterval(() => {
        fetch("/status", { method: "GET" })
            .then((response) => {
                return response.text();
            }).then((response_text) => {
                console.log("Answer got:", response_text);
                switch (response_text) {
                    case "0":
                        if (bar_size < 10) bar_size += 11;
                        break;
                    case "1":
                        bar_size = 10;
                        if (bar_size < 60) bar_size += 10;
                        break;
                    case "2":
                        bar_size = 60;
                        if (bar_size < 90) bar_size += 10;
                        break;
                    case "3":
                        bar_size = 100;
                        break;
                }
                $("#uploading_progress").css("width", bar_size + "%").attr('aria-valuenow', bar_size);
            });
    }, 100);
}

/*
return "Что-то пошло не так"
        elif parser.get_state() == 0:
            return "Презентация поступает в обработку"
        elif parser.get_state() == 1:
            return "Презентация загружается"
        elif parser.get_state() == 2:
            return "Презентация загружена"
        elif parser.get_state() == 3:
            return "Презентация обработана"
 */

function criteria() {
    window.location.href = "/criteria";
}

function debug() {

    return false;
}

function check() {

}