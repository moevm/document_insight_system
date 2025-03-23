function clearSessionLocalStorage() {
    [
        'template_file', 'data_file', 'table_preview',
        'verification_result', 'generated_files', 'naming_template', 'naming_fields',
        'currentActivatedTab'
    ].forEach(e => localStorage.removeItem(e))
}

function loadFromStorage() {
    // check validity
    if (localStorage.getItem('template_file')) {
        let json = JSON.parse(localStorage.getItem('template_file'));
        // check if this file expired or not, if expired then clear session
        if (Date.now() > Date.parse(json.expire_at + 'Z')) {
            clearSessionLocalStorage()
            return;
        }
    }
    if (localStorage.getItem('data_file')) {
        let json = JSON.parse(localStorage.getItem('data_file'))
        if (Date.now() > Date.parse(json.expire_at + 'Z')) {
            clearSessionLocalStorage()
            return;
        }
    }
    // restore form state
    if (localStorage.getItem('template_file')) {
        let json = JSON.parse(localStorage.getItem('template_file'))
        template_id = json.id
        template_name = json.name
        showTemplatePreview()
        activeTabDataTable(false)
    }
    if (localStorage.getItem('data_file')) {
        let json = JSON.parse(localStorage.getItem('data_file'))
        data_table_id = json.id
        showDataPreview()
    }
    if (localStorage.getItem('verification_result')) {
        activeTabRender(false)
        let div_verification = document.getElementById('verificationResult')

        let input_name_template = document.getElementById('filename-template')

        let div_fields = document.getElementById('field-list')

        div_verification.innerHTML = localStorage.getItem('verification_result')
        input_name_template.value = localStorage.getItem('naming_template')
        div_fields.innerHTML = localStorage.getItem('naming_fields')
    }
    if (localStorage.getItem('generated_files')) {
        activeTabResult(false)
        let div_result = document.getElementById('render-result')

        div_result.innerHTML = localStorage.getItem('generated_files')
    }
    $('#' + localStorage.getItem('currentActivatedTab')).tab('show')
}