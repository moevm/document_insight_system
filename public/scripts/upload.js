function send1() {
    let presentation = document.getElementById("upload_file").files[0];
    let formData = new FormData();
    formData.append("presentation", presentation);
    fetch('/criteria', {method: "POST", body: formData})
    window.location = "/criteria";
}

function send2() {
    window.location = "/results";
}