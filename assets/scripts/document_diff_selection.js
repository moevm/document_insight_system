const FILTERS = ['filter_filename', 'filter_id', 'filter_student', 'filter_criteria', 'filter_date_from', 'filter_date_to', 'filter_score_from', 'filter_score_to'];

function addCell(row, value) {
    const cell = document.createElement('td');
    cell.textContent = value || '-';
    row.appendChild(cell);
}

export function initDocumentSelection(form) {
    const rows = document.getElementById('document-diff-rows');
    const error = document.getElementById('document-diff-error');
    const panel = document.getElementById('system-document-search');
    const filters = document.getElementById('system-document-filters');
    const compare = document.getElementById('start-document-diff');
    let activeSide, timer;
    const clearError = () => error.classList.add('d-none');
    const showError = message => { error.textContent = message; error.classList.remove('d-none'); };
    const update = () => {
        compare.disabled = !['first', 'second'].every(side => document.getElementById(`${side}-file`).files.length || document.getElementById(`${side}-document-id`).value);
    };
    const render = items => {
        rows.replaceChildren();
        if (!items.length) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 7; cell.className = 'text-center'; cell.textContent = 'Документы не найдены.';
            row.appendChild(cell); rows.appendChild(row); return;
        }
        items.forEach(item => {
            const row = document.createElement('tr');
            const button = document.createElement('button');
            button.type = 'button'; button.className = 'btn btn-secondary btn-sm'; button.textContent = 'Выбрать';
            button.addEventListener('click', () => {
                document.getElementById(`${activeSide}-document-id`).value = item._id;
                document.getElementById(`${activeSide}-file`).value = '';
                document.getElementById(`${activeSide}-document-name`).textContent = item.filename;
                panel.classList.add('d-none');
                update();
            });
            const cell = document.createElement('td'); cell.appendChild(button); row.appendChild(cell);
            [item._id, item.filename, item.student, item.criteria, item['upload-date'], item.score].forEach(value => addCell(row, value));
            rows.appendChild(row);
        });
    };
    const load = () => {
        clearError(); const query = new URLSearchParams({ format: form.elements.format.value });
        FILTERS.forEach(name => form.elements[name].value && query.set(name, form.elements[name].value));
        fetch(`/document_diff/data?${query}`).then(async response => {
            const data = await response.json(); if (!response.ok) throw Error(data.error); return data;
        }).then(data => render(data.rows)).catch(exception => showError(exception.message));
    };
    document.querySelectorAll('.find-system-document').forEach(button => button.addEventListener('click', () => {
        activeSide = button.dataset.side; document.getElementById('system-document-search-title').textContent = `Поиск для: ${button.dataset.label}`;
        panel.classList.remove('d-none');
        filters.classList.remove('d-none');
        rows.replaceChildren();
        clearError();
    }));
    ['first', 'second'].forEach(side => document.getElementById(`${side}-file`).addEventListener('change', event => {
        if (event.target.files[0]) { document.getElementById(`${side}-document-id`).value = ''; document.getElementById(`${side}-document-name`).textContent = event.target.files[0].name; update(); }
    }));
    form.querySelectorAll('input[name="format"]').forEach(input => input.addEventListener('change', () => {
        const accepted = input.value === 'pptx' ? '.ppt,.pptx,.odp' : '.doc,.docx,.md,.odt';
        ['first', 'second'].forEach(side => { document.getElementById(`${side}-file`).accept = accepted; document.getElementById(`${side}-file`).value = ''; document.getElementById(`${side}-document-id`).value = ''; }); update();
    }));
    document.getElementById('find-system-documents').addEventListener('click', load);
    document.getElementById('reset-system-document-filters').addEventListener('click', () => { FILTERS.forEach(name => form.elements[name].value = ''); rows.replaceChildren(); clearError(); });
    document.getElementById('filter-student').addEventListener('input', event => {
        clearTimeout(timer); timer = setTimeout(() => fetch(`/document_diff/student-suggestions?query=${encodeURIComponent(event.target.value)}`).then(response => response.json()).then(data => {
            const list = document.getElementById('student-suggestions'); list.replaceChildren(); data.items.forEach(item => { const option = document.createElement('option'); option.value = item; list.appendChild(option); });
        }), 250);
    });
    update();
}