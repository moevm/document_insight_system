window.onload = function() {
    loadFromStorage();

    // Загружаем шаблоны из базы
    fetch('/api/templates')
        .then(res => res.json())
        .then(data => {
            if (data.templates && data.templates.length > 0) {
                renderTemplateSelector(data.templates);
            }
        })
        .catch(err => console.error("Ошибка загрузки шаблонов из БД:", err));

    // Загружаем таблицы данных из базы
    fetch('/api/data-files')
        .then(res => res.json())
        .then(data => {
            if (data.files && data.files.length > 0) {
                const select = document.getElementById("data-table-select");
                if (!select) {
                    console.warn("⚠️ #data-table-select не найден в DOM");
                    return;
                }
                data.files.forEach(file => {
                    const option = document.createElement("option");
                    option.value = file.id;
                    option.textContent = `${file.name} (${file.uploaded})`;
                    select.appendChild(option);
                });
            }
        })
        .catch(err => console.error("Ошибка загрузки таблиц из БД:", err));

    // Обработчик поля шаблона имени файла
    document.getElementById('filename-template').onchange = onFilenameTemplateChange;

    // Сохраняем активную вкладку
    $('#pills-template-tab, #pills-datatable-tab, #pills-render-tab, #pills-result-tab').click(function(event) {
        localStorage.setItem('currentActivatedTab', event.target.id);
    });
};


function renderTemplateSelector(templates) {
    const select = document.getElementById("template-select");
    if (!select) {
        console.warn("⚠️ #template-select не найден в DOM");
        return;
    }

    templates.forEach(template => {
        const option = document.createElement("option");
        option.value = template.id; // предполагается, что это file_id
        option.textContent = `${template.name} (${template.file_format})`;
        select.appendChild(option);
    });
}

function useSelectedDataTable() {
    const select = document.getElementById("data-table-select");
    const fileId = select.value;

    if (!fileId) {
        alert("Выберите таблицу данных.");
        return;
    }

    sessionStorage.setItem("dataId", fileId);
    document.getElementById("data-table-file").dataset.fileId = fileId;

    document.getElementById("data-next-group").classList.remove("d-none");
    $('#data-table-preview').removeClass('d-none');
    $('#btn-upload-data').removeClass('btn-primary').addClass('btn-secondary');

    document.getElementById("div-data-table-preview").innerHTML = "<i>Таблица выбрана из базы. Предпросмотр не отображается.</i>";
}




function upload(file, callback, processBar, tablePreview = false) {
    if (file.size > 15 * 1024 * 1024) {
        alert('File too large');
        return;
    }
    var formData = new FormData();

    formData.append("file", file);
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
        console.log('Response:', req.response);

        // Проверяем, является ли ответ JSON
        try {
            var responseJSON = JSON.parse(req.response); // Попытка парсинга JSON
            console.log(responseJSON);

            if (req.status == 200) {
                callback(responseJSON);  // Обработка корректного ответа
                console.log("Uploaded!");
            } else {
                alert('Error occurred when trying to upload your file: ' + req.response);
                console.log("Error " + req.status + " occurred when trying to upload your file.<br \/>");
            }
        } catch (e) {
            // Если ошибка при парсинге JSON
            console.log('Failed to parse JSON:', e);
            console.log('Server Response:', req.response);
            alert('Server returned an unexpected response format.');
        }
    };

    req.send(formData);
}


function uploadTemplate() {
    const fileInput = document.getElementById("template-file");
    const file = fileInput.files[0];
    if (!file) {
        alert("Выберите файл шаблона.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    fetch("/upload", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(response => {
        if (response.status === "OK") {
            // ✅ ВСТАВИТЬ ВОТ ЗДЕСЬ:
            document.getElementById("template-file").dataset.fileId = response.file_id;
            sessionStorage.setItem("templateId", response.file_id);

            // Показать кнопку "Use this template" и превью
            document.getElementById("template-next-group").classList.remove("d-none");
            const iframe = document.getElementById("iframe-template-preview");
            iframe.src = `/preview?file_id=${response.file_id}`;
            document.getElementById("template-preview").classList.remove("d-none");
        } else {
            alert("Ошибка загрузки шаблона.");
        }
    })
    .catch(err => {
        console.error("Ошибка загрузки:", err);
        alert("Произошла ошибка при загрузке шаблона.");
    });
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

function getTemplateId() {
    const input = document.getElementById("template-file");
    if (input && input.files && input.files.length > 0 && input.dataset.fileId) {
        return input.dataset.fileId;
    }

    // ✅ берём ID из sessionStorage, если выбрано из БД
    return sessionStorage.getItem("templateId");
}


function useSelectedTemplate() {
    const select = document.getElementById("template-select");
    const fileId = select.value;

    if (!fileId) {
        alert("Выберите шаблон.");
        return;
    }

    // Сохраняем ID для дальнейшей генерации
    sessionStorage.setItem("templateId", fileId);
    document.getElementById("template-file").dataset.fileId = fileId;

    // Отображаем кнопку "Use this template"
    document.getElementById("template-next-group").classList.remove("d-none");
    document.getElementById("template-preview").classList.remove("d-none");

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
        
        sessionStorage.setItem("dataId", res.file_id);
        document.getElementById("data-table-file").dataset.fileId = res.file_id;

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

function getDataId() {
    const input = document.getElementById("data-table-file");
    if (input && input.files && input.files.length > 0 && input.dataset.fileId) {
        return input.dataset.fileId;
    }
    return sessionStorage.getItem("dataId");
}


function showDataPreview() {
    $('#div-data-table-preview').html(localStorage.getItem('table_preview'))

    $('#data-next-group, #data-table-preview').toggleClass('d-none', false);
    $('#btn-upload-data').toggleClass('btn-primary', false).toggleClass('btn-secondary', true)
}

function activeTabDataTable(updateStorage = true) {
    const templateId = getTemplateId(); // получить ID шаблона

    if (templateId) {
        var pills_tab = $('#pills-datatable-tab');
        pills_tab.toggleClass('disabled', false);
        if (updateStorage) {
            pills_tab.tab('show');
            localStorage.setItem('currentActivatedTab', 'pills-datatable-tab');
        }
    } else {
        alert("Шаблон не выбран.");
    }
}


async function uploadArchiveToGoogleDrive() {
    try {
        const archiveLink = document.querySelector('#link-archive a');
        if (!archiveLink) {
            alert('Архив не найден для загрузки');
            return;
        }

        const urlParams = new URLSearchParams(new URL(archiveLink.href).search);
        const file_id = urlParams.get('file_id');
        if (!file_id) {
            alert('Не удалось получить ID файла архива');
            return;
        }

        // Заблокируем кнопку, покажем загрузку
        const btn = document.querySelector("input[value='Загрузить в Google Drive']");
        btn.disabled = true;
        btn.value = "Загрузка...";

        const response = await fetch('/export_archive_to_drive', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({file_id})
        });

        const result = await response.json();

        if (response.ok) {
            alert('Архив успешно загружен в Google Drive');
        } else {
            alert('Ошибка при загрузке: ' + (result.error || 'Неизвестная ошибка'));
        }
    } catch (e) {
        alert('Ошибка при загрузке в Google Drive: ' + e.message);
    } finally {
        const btn = document.querySelector("input[value='Загрузка...']");
        if (btn) {
            btn.disabled = false;
            btn.value = 'Загрузить в Google Drive';
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
    // Очистка sessionStorage
    sessionStorage.removeItem("templateId");
    sessionStorage.removeItem("dataId");

    // Очистка глобальных переменных (если они есть)
    template_id = null;
    template_name = null;
    data_table_id = null;
    
    clearSessionLocalStorage();
    
    $('#pills-template-tab').tab('show');
    $('#pills-datatable-tab, #pills-render-tab, #pills-result-tab').toggleClass('disabled', true);
    $('#template-next-group, #data-next-group, #template-preview, #data-table-preview').toggleClass('d-none', true);

    $('#iframe-template-preview, #iframe-data-table-preview').attr('src', "about:blank")
    $('#progress-template, #progress-data-table').val(0);

    $('#btn-upload-template, #btn-upload-data').toggleClass('btn-primary', true).toggleClass('btn-secondary', false);
}


function appendJinjaTag(element) {
    let input = document.getElementById('filename-template')
    input.value += `{{ ${element.value} }}`
    input.onchange();
}

function verifyTemplate() {
    const templateId = getTemplateId();
    const dataId = getDataId();

    if (!templateId || !dataId) {
        alert("Шаблон и таблица данных должны быть выбраны.");
        return;
    }

    $('#loadingModal').modal('show');

    const formData = new FormData();
    formData.append("template-id", templateId);
    formData.append("data-table-id", dataId);
    formData.append("name-pattern", dataId);  // если реально нужно

    const req = new XMLHttpRequest();
    req.open("POST", "/verify", true);

    req.onload = function(event) {
        console.log(req.response);
        if (req.status == 200) {
            const res = JSON.parse(req.response);

            if (res.status === 'err') {
                alert('Something went wrong: ' + req.response);
            } else {
                const divVerification = document.getElementById('verificationResult');
                divVerification.innerHTML = '';
                for (const message of res.messages) {
                    divVerification.innerHTML += `<p>${message}</p>`;
                }

                const inputNameTemplate = document.getElementById('filename-template');
                inputNameTemplate.value = `{{ ${res.fields[0]} }}`;

                const divFields = document.getElementById('field-list');
                divFields.innerHTML = '';
                for (const field of res.fields) {
                    divFields.innerHTML += `<input type='button' onclick='appendJinjaTag(this)' value='${field}'/>`;
                }

                localStorage.setItem('verification_result', divVerification.innerHTML);
                localStorage.setItem('naming_template', inputNameTemplate.value);
                localStorage.setItem('naming_fields', divFields.innerHTML);

                activeTabRender();
            }
        } else {
            console.log("Error " + req.status + " occurred");
        }

        setTimeout(() => $('#loadingModal').modal('hide'), 500);
    };

    req.send(formData);
}


function activeTabRender() {
    const renderTab = $('#pills-render-tab');

    renderTab.removeClass('disabled');
    renderTab.tab('show'); // переключение Bootstrap-вкладки

    localStorage.setItem('currentActivatedTab', 'pills-render-tab');
}


function getTemplateId() {
    const input = document.getElementById("template-file");
    if (input && input.files && input.files.length > 0 && input.dataset.fileId) {
        return input.dataset.fileId;
    }
    return sessionStorage.getItem("templateId");
}

function generateResult() {
    const templateId = getTemplateId();
    const dataId = getDataId();

    if (!templateId) {
        alert("Шаблон не выбран.");
        return;
    }

    if (!dataId) {
        alert("Таблица данных не выбрана.");
        return;
    }

    const namePattern = document.getElementById("filename-template").value;

    const formData = new FormData();
    formData.append("template-id", templateId);
    formData.append("data-table-id", dataId);
    formData.append("name-pattern", namePattern);

    fetch("/render", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "OK") {
            console.log("Результат готов:", data);

            // ✅ Переход на вкладку "Download"
            activeTabResult();

            // ✅ Отобразить ссылки на отдельные файлы
            const linksContainer = document.getElementById("link-files");
            linksContainer.innerHTML = "<ul>";

            for (const [filename, fileId] of Object.entries(data.files)) {
                linksContainer.innerHTML += `<li><a href="/files?file_id=${fileId}" target="_blank">${filename}</a></li>`;
            }

            linksContainer.innerHTML += "</ul>";

            // ✅ Отобразить ссылку на архив, если он есть
            const archiveLink = document.getElementById("link-archive");
            if (data.archive && data.archive_name) {
                archiveLink.innerHTML = `<a href="/files?file_id=${data.archive}" target="_blank">${data.archive_name}</a>`;
            } else {
                archiveLink.innerText = "—";
            }
        } else {
            alert("Ошибка генерации.");
        }
    })
    .catch(err => {
        console.error("Ошибка:", err);
        alert("Ошибка при генерации.");
    });
}



function onFilenameTemplateChange() {
    localStorage.setItem('naming_template', document.getElementById('filename-template').value)
}
