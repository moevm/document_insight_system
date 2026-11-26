const FILTERS = ['filter_filename', 'filter_id', 'filter_student', 'filter_criteria', 'filter_date_from', 'filter_date_to', 'filter_score_from', 'filter_score_to'];
const ACTIVE_SIDE = 'active_side';
const SIDES = ['first', 'second'];

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
    const savedParams = new URLSearchParams(window.location.search);
    let activeSide = SIDES.includes(savedParams.get(ACTIVE_SIDE)) ? savedParams.get(ACTIVE_SIDE) : 'first';
    let timer;
    const clearError = () => error.classList.add('d-none');
    const showError = message => { error.textContent = message; error.classList.remove('d-none'); };
    const resetFilters = () => FILTERS.forEach(name => { form.elements[name].value = ''; });
    const openSearch = side => {
        activeSide = side;
        const button = document.querySelector(`.find-system-document[data-side="${side}"]`);
        document.getElementById('system-document-search-title').textContent = `Поиск для: ${button ? button.dataset.label : side}`;
        panel.classList.remove('d-none');
        filters.classList.remove('d-none');
    };
    const savedFormat = savedParams.get('format');
    const hasSavedFilters = FILTERS.some(name => savedParams.has(name));
    if (savedFormat === 'docx' || savedFormat === 'pptx') {
        const formatInput = form.querySelector(`input[name="format"][value="${savedFormat}"]`);
        formatInput.checked = true;
        form.querySelectorAll('#format-toggle label').forEach(label => {
            label.classList.toggle('active', label.contains(formatInput));
        });
    }
    FILTERS.forEach(name => {
        form.elements[name].value = savedParams.get(name) || '';
    });
    SIDES.forEach(side => {
        const documentId = savedParams.get(`${side}_document_id`);
        if (documentId) {
            document.getElementById(`${side}-document-id`).value = documentId;
            document.getElementById(`${side}-document-name`).textContent = savedParams.get(`${side}_document_name`) || documentId;
        }
    });
    const update = () => {
        compare.disabled = !SIDES.every(side => document.getElementById(`${side}-file`).files.length || document.getElementById(`${side}-document-id`).value);
    };
    const getSearchParams = () => {
        const query = new URLSearchParams({ format: form.elements.format.value, [ACTIVE_SIDE]: activeSide });
        FILTERS.forEach(name => form.elements[name].value && query.set(name, form.elements[name].value));
        SIDES.forEach(side => {
            const documentId = document.getElementById(`${side}-document-id`).value;
            if (documentId) {
                query.set(`${side}_document_id`, documentId);
                query.set(`${side}_document_name`, document.getElementById(`${side}-document-name`).textContent);
            }
        });
        return query;
    };
    const saveSearchState = () => {
        window.history.replaceState({}, '', `${window.location.pathname}?${getSearchParams()}`);
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
                resetFilters();
                rows.replaceChildren();
                clearError();
                saveSearchState();
                panel.classList.add('d-none');
                update();
            });
            const cell = document.createElement('td'); cell.appendChild(button); row.appendChild(cell);
            [item._id, item.filename, item.student, item.criteria, item['upload-date'], item.score].forEach(value => addCell(row, value));
            rows.appendChild(row);
        });
    };
    const load = () => {
        clearError();
        saveSearchState();
        const query = new URLSearchParams({ format: form.elements.format.value });
        FILTERS.forEach(name => form.elements[name].value && query.set(name, form.elements[name].value));
        fetch(`/document_diff/data?${query}`).then(async response => {
            const data = await response.json(); if (!response.ok) throw Error(data.error); return data;
        }).then(data => render(data.rows)).catch(exception => showError(exception.message));
    };
    document.querySelectorAll('.find-system-document').forEach(button => button.addEventListener('click', () => {
        openSearch(button.dataset.side);
        saveSearchState();
        rows.replaceChildren();
        clearError();
    }));
    SIDES.forEach(side => document.getElementById(`${side}-file`).addEventListener('change', event => {
        if (event.target.files[0]) { document.getElementById(`${side}-document-id`).value = ''; document.getElementById(`${side}-document-name`).textContent = event.target.files[0].name; saveSearchState(); update(); }
    }));
    form.querySelectorAll('input[name="format"]').forEach(input => input.addEventListener('change', () => {
        const accepted = input.value === 'pptx' ? '.ppt,.pptx,.odp' : '.doc,.docx,.md,.odt';
        SIDES.forEach(side => { document.getElementById(`${side}-file`).accept = accepted; document.getElementById(`${side}-file`).value = ''; document.getElementById(`${side}-document-id`).value = ''; document.getElementById(`${side}-document-name`).textContent = 'Документ не выбран'; }); saveSearchState(); update();
    }));
    document.getElementById('find-system-documents').addEventListener('click', load);
    document.getElementById('reset-system-document-filters').addEventListener('click', () => {
        resetFilters();
        saveSearchState();
        rows.replaceChildren();
        clearError();
    });
    document.getElementById('filter-student').addEventListener('input', event => {
        clearTimeout(timer); timer = setTimeout(() => fetch(`/document_diff/student-suggestions?query=${encodeURIComponent(event.target.value)}`).then(response => response.json()).then(data => {
            const list = document.getElementById('student-suggestions'); list.replaceChildren(); data.items.forEach(item => { const option = document.createElement('option'); option.value = item; list.appendChild(option); });
        }), 250);
    });
    update();
    const activeSideSelected = Boolean(document.getElementById(`${activeSide}-document-id`).value);
    if (hasSavedFilters && !activeSideSelected) {
        openSearch(activeSide);
        load();
    }
}