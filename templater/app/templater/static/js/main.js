let template_id;
let data_table_id;
let template_name;
let recaptcha_site_key = RECAPTCHA_SITE_KEY

function upload(file, callback, processBar, tablePreview = false) {
    grecaptcha.ready(function() {
        grecaptcha.execute(recaptcha_site_key, { action: 'upload' }).then(function(token) {
            // let url = window.location.origin + "/upload"
            if (file.size > 15 * 1024 * 1024) {
                alert('File too large');
                return;
            }
            var formData = new FormData();

            formData.append("file", file);
            formData.append("recaptcha-token", token);
            if (tablePreview) {
                formData.append('table-preview', true)
            }
            var req = new XMLHttpRequest();
            req.upload.addEventListener("progress", function(event) {
                var percent = (event.loaded / event.total) * 100;
                console.log(percent)
                processBar.val(Math.round(percent));
            }, false);

            req.open("POST", "/upload", true);

            req.onload = function(event) {
                console.log(req.response);
                if (req.status == 200) {
                    console.log(req.response);
                    console.log(JSON.parse(req.response));
                    callback(JSON.parse(req.response));
                    console.log("Uploaded!");
                } else {
                    alert('Error occured when trying to upload your file: '+req.response)
                    console.log("Error " + req.status + " occurred when trying to upload your file.<br \/>");
                }
            };
            req.send(formData);
        });
    });
}

function uploadTemplate() {
    // check if no file chosen, or extension not supported
    if ($('#template-file')[0].files.length == 0) {
        alert("No file chosen");
        return;
    }
    let file = $('#template-file')[0].files[0];
    if (['docx', 'odt', 'ods', 'odp', 'pptx', 'xlsx'].indexOf(file.name.split('.').pop()) == -1) {
        console.log(file.name.split('.').pop())
        alert("File extension is not supported");
        return;
    }
    $('#progress-template').val(0)
    upload(file, function(res) {
        template_id = res.file_id;
        template_name = res.file_name;
        // save in local storage
        localStorage.setItem('template_file', JSON.stringify({ id: template_id, name: template_name, expire_at: res.expire_at }))
        $('#pills-render-tab, #pills-result-tab').toggleClass('disabled', true);

        showTemplatePreview()
    }, $('#progress-template'))
}

function showTemplatePreview() {
    $('#template-next-group, #template-preview').toggleClass('d-none', false);
    $('#btn-upload-template').toggleClass('btn-primary', false).toggleClass('btn-secondary', true)

    // show preview using gg docs (not available on localhost) for types and ViewerJS for others 
    let ifrm = document.createElement("iframe");
    ifrm.setAttribute("id", 'iframe-template-preview');
    ifrm.style.width = "100%";
    ifrm.style.height = "500px";

    if (['docx', 'pptx', 'xlsx'].indexOf(template_name.split('.').pop()) != -1) {
        let url = "https://docs.google.com/gview?url=" + window.location.origin + "/files?file_id=" + template_id + "&embedded=true";
        if (window.location.hostname != "localhost") {
            ifrm.setAttribute("src", url);
        } else {
            console.log(url)
        }
    } else if (['ods', 'odp', 'odt'].indexOf(template_name.split('.').pop()) != -1) {
        let url = window.location.origin + "/ViewerJS/#../files?file_id=" + template_id;
        console.log(url);
        ifrm.setAttribute("src", url);
    }
    let container = document.getElementById('preview-container')
    container.innerHTML = ''
    container.appendChild(ifrm)
}

function uploadData() {
    // check if no file chosen, or extension not supported
    if ($('#data-table-file')[0].files.length == 0) {
        alert("No file chosen");
        return;
    }
    let file = $('#data-table-file')[0].files[0]
    if (['xlsx', 'csv', 'xls'].indexOf(file.name.split('.').pop()) == -1) {
        alert("File extension is not supported");
        return;
    }

    $('#progress-data-table').val(0)
    upload(file, function(res) {
        data_table_id = res.file_id;

        // save in local storage
        localStorage.setItem('data_file', JSON.stringify({ id: data_table_id, expire_at: res.expire_at }))
        $('#pills-render-tab, #pills-result-tab').toggleClass('disabled', true);

        // show data table from vals returned from server
        let table = `<table class='table table-bordered'>`
        res.data.reduce(function(accumulator, current, index) {
            table += '<tr>'
            if (index == 0) {
                for (val of current) {
                    table += `<th>${val}</th>`
                }
            } else {
                for (val of current) {
                    table += `<td>${val}</td>`
                }
            }
            table += '</tr>'
        }, table)
        table += '</table>'

        localStorage.setItem('table_preview', table)

        showDataPreview()
    }, $('#progress-data-table'), true)
}

function showDataPreview() {
    $('#div-data-table-preview').html(localStorage.getItem('table_preview'))

    $('#data-next-group, #data-table-preview').toggleClass('d-none', false);
    $('#btn-upload-data').toggleClass('btn-primary', false).toggleClass('btn-secondary', true)
}

function activeTabDataTable(updateStorage = true) {
    if (template_id) {
        var pills_tab = $('#pills-datatable-tab');
        pills_tab.toggleClass('disabled', false);
        if (updateStorage) {
            pills_tab.tab('show');
            localStorage.setItem('currentActivatedTab', 'pills-datatable-tab');
        }
    }
}

function activeTabRender(updateStorage = true) {
    if (data_table_id) {
        var pills_tab = $('#pills-render-tab');
        pills_tab.toggleClass('disabled', false);
        if (updateStorage) {
            pills_tab.tab('show');
            localStorage.setItem('currentActivatedTab', 'pills-render-tab');
        }
    }
}

function activeTabResult(updateStorage = true) {
    var pills_tab = $('#pills-result-tab');
    pills_tab.toggleClass('disabled', false);
    if (updateStorage) {
        pills_tab.tab('show');
        localStorage.setItem('currentActivatedTab', 'pills-result-tab');
    }
}

function resetForms() {
    template_id = null;
    template_name = null;
    data_table_id = null;
    clearSessionLocalStorage()
    $('#pills-template-tab').tab('show');
    $('#pills-datatable-tab, #pills-render-tab, #pills-result-tab').toggleClass('disabled', true);
    $('#template-next-group, #data-next-group, #template-preview, #data-table-preview').toggleClass('d-none', true);

    $('#iframe-template-preview, #iframe-data-table-preview').attr('src', "about:blank")
    $('#progress-template, #progress-data-table').val(0);

    $('#btn-upload-template, #btn-upload-data').toggleClass('btn-primary', true).toggleClass('btn-secondary', false)

}

function appendJinjaTag(element) {
    let input = document.getElementById('filename-template')
    input.value += `{{ ${element.value} }}`
    input.onchange();
}

function verifyTemplate() {
    if (!template_id || !data_table_id) return;
    grecaptcha.ready(function() {
        grecaptcha.execute(recaptcha_site_key, { action: 'validate' }).then(function(token) {
            $('#loadingModal').modal('show')
                // send request to verify-url with template_id and data_table_id and put result to #verificationResult
            var formData = new FormData();

            formData.append("template-id", template_id);
            formData.append("data-table-id", data_table_id);

            formData.append("name-pattern", data_table_id);
            formData.append("recaptcha-token", token);
            // TODO: default if cookie not set??

            function getLocale() {
                const def_val = 'ru'
                if (document.cookie) {
                    let entry = document.cookie
                        .split('; ')
                        .find(row => row.startsWith('_LOCALE_'))
                    if (entry) return entry.split('=')[1];
                    else return def_val
                } else return def_val
            }

            var req = new XMLHttpRequest();

            req.open("POST", "/verify?_LOCALE_=" + getLocale(), true);

            req.onload = function(event) {
                console.log(req.response)
                if (req.status == 200) {
                    var res = JSON.parse(req.response)

                    if (res.status == 'err') {
                        alert('Something wrong occurred: '+req.response)
                    } else {

                        let div_verification = document.getElementById('verificationResult')

                        div_verification.innerHTML = ''
                        for (message of res.messages) {
                            div_verification.innerHTML += `<p>${message}</p>`
                        }

                        let input_name_template = document.getElementById('filename-template')
                        input_name_template.value = `{{ ${res.fields[0]} }}`

                        let div_fields = document.getElementById('field-list')
                        div_fields.innerHTML = ''
                        for (field of res.fields) {
                            div_fields.innerHTML += `<input type='button' onclick='appendJinjaTag(this)' value='${field}'/>`
                        }

                        localStorage.setItem('verification_result', div_verification.innerHTML)
                        localStorage.setItem('naming_template', input_name_template.value)
                        localStorage.setItem('naming_fields', div_fields.innerHTML)
                        activeTabRender()
                    }
                } else {
                    console.log("Error " + req.status + " occurred");
                }
                setTimeout(function() { $('#loadingModal').modal('hide') }, 500);
            };
            req.send(formData);
        });
    });
}

function generateResult() {
    if (!template_id || !data_table_id) return;
    grecaptcha.ready(function() {
        grecaptcha.execute(recaptcha_site_key, { action: 'generateResult' }).then(function(token) {
            $('#loadingModal').modal('show')
                // send request to render-url with template_id and data_table_id and put result to #render-result
            var formData = new FormData();

            formData.append("template-id", template_id);
            formData.append("data-table-id", data_table_id);
            let name_template = document.getElementById('filename-template').value;
            if (name_template.length != 0) {
                formData.append("name-pattern", name_template);
            }
            formData.append("recaptcha-token", token);
            var req = new XMLHttpRequest();

            req.open("POST", "/render", true);

            req.onload = function(event) {
                console.log(req.response)
                if (req.status == 200) {
                    var res = JSON.parse(req.response)

                    if (res.status == 'err') {
                        alert('Something wrong occurred: '+req.response)
                    } else {

                        let div_result = document.getElementById('render-result')
                            //div_result.innerHTML = 'Generated files:<br /><ul>'
                        let div_files = document.getElementById('link-files');

                        let link_files = "<ul>"
                            // div_files.innerHTML = '<ul>'

                        for (let filename in res.files) {
                            // div_files.innerHTML += `<li><a href='/files?file_id=${res.files[filename]}'>${filename}</a></li>`
                            link_files += `<li><a href='/files?file_id=${res.files[filename]}'>${filename}</a></li>`
                        };
                        link_files += "</ul>"
                        div_files.innerHTML = link_files

                        let div_archive = document.getElementById('link-archive');
                        div_archive.innerHTML = `<a href='/files?file_id=${res.archive}'>${res.archive_name}</a>`

                        localStorage.setItem('generated_files', div_result.innerHTML)

                        activeTabResult()
                    }
                } else {
                    console.log("Error " + req.status + " occurred");
                }
                setTimeout(function() { $('#loadingModal').modal('hide') }, 500);
            };
            req.send(formData);
        });
    });
}

function onFilenameTemplateChange() {
    localStorage.setItem('naming_template', document.getElementById('filename-template').value)
}

// try to load session from localStorage
window.onload = function() {
    loadFromStorage()
    document.getElementById('filename-template').onchange = onFilenameTemplateChange
    $('#pills-template-tab, #pills-datatable-tab, #pills-render-tab, #pills-result-tab').click(function(event) {
        localStorage.setItem('currentActivatedTab', event.target.id);
    })
};
