(async () => {
    const frame = document.querySelector('iframe');
    const report = document.querySelector('#result');
    const checks = [];
    let page;
    const assert = (condition, label) => { if (!condition) throw new Error(label); checks.push(label); };
    const wait = (fn, label) => new Promise((resolve, reject) => {
        const start = Date.now();
        const poll = () => {
            try { if (fn()) { resolve(); return; } } catch (_) { /* iframe is navigating */ }
            if (Date.now() - start > 5000) { reject(new Error(`Timeout: ${label}`)); return; }
            setTimeout(poll, 25);
        };
        poll();
    });
    const load = async path => {
        await new Promise(resolve => { frame.onload = resolve; frame.src = path; });
        await wait(() => frame.contentWindow.location.pathname === path.split('?')[0] && frame.contentDocument.querySelector('.data-table-panel') && frame.contentDocument.querySelector('tbody tr[data-index]'), path);
        page = frame.contentWindow;
    };
    const elements = selector => [...page.document.querySelectorAll(selector)];
    const button = label => elements('.table-actions button').find(el => el.textContent === label);
    const input = (selector, value, event = 'input') => {
        const element = page.document.querySelector(selector);
        element.value = value;
        element.dispatchEvent(new page.Event(event, { bubbles: true }));
    };
    try {
        await load('/users/');
        assert(elements('tbody tr[data-index]').length === 25, 'user page size');
        assert(elements('tbody img').length === 0 && !page.injected, 'user values escaped');
        assert(elements('.keep-open button').length === 1, 'column picker');
        elements('.keep-open button')[0].click();
        elements('.keep-open input[data-field=name]')[0].click();
        assert(elements('thead th[data-field=name]').length === 0, 'hide column');
        elements('.keep-open input[data-field=name]')[0].click();
        assert(elements('thead th[data-field=name]').length === 1, 'restore column');
        button('Фильтры').click();
        // Filter inputs own data-field; header cells use the same attribute.
        input('.table-filters select[data-field=role]', 'admin', 'change');
        await wait(() => elements('tbody tr[data-index]').length === 18, 'role filter');
        assert(JSON.parse(new URLSearchParams(page.location.search).get('filter')).role === 'admin', 'filters in URL');
        input('.table-search', 'User 3');
        await wait(() => elements('tbody tr[data-index]').length === 3, 'combined search and role');
        const saved = page.location.pathname + page.location.search;
        const previousDocument = frame.contentDocument;
        page.history.back();
        await wait(() => frame.contentDocument !== previousDocument && !new URLSearchParams(frame.contentWindow.location.search).has('search') && frame.contentDocument.querySelectorAll('tbody tr[data-index]').length === 18, 'history back');
        await load(saved);
        assert(elements('.table-search')[0].value === 'User 3', 'search restored');
        assert(elements('.table-filters select[data-field=role]')[0].value === 'admin', 'role restored');
        button('Сбросить').click();
        await wait(() => elements('tbody tr[data-index]').length === 25, 'reset filters');
        elements('.page-list button')[0].click();
        elements('.page-list .dropdown-item').find(el => el.textContent.trim() === '10').click();
        await wait(() => elements('tbody tr[data-index]').length === 10, 'page size');
        elements('.page-next a')[0].click();
        await wait(() => new URLSearchParams(page.location.search).get('offset') === '10', 'pagination URL');
        assert(elements('tbody tr[data-index]').length === 10, 'pagination rows');
        elements('th[data-field=name] .th-inner')[0].click();
        await wait(() => new URLSearchParams(page.location.search).get('sort') === 'name', 'sorting URL');
        input('.table-search', 'error');
        await wait(() => !elements('.table-error')[0].hidden, 'request error');
        assert(elements('.table-error')[0].textContent.includes('Тестовая ошибка'), 'visible error');
        button('Сбросить').click();
        await wait(() => elements('tbody tr[data-index]').length === 10 && elements('.table-error')[0].hidden, 'recover after error');
        await load('/check_list/?filter_user=student&filter_score=0.5-1&latest=1');
        assert(button('Последние проверки').getAttribute('aria-pressed') === 'true', 'latest restored');
        assert(elements('.table-filters input[data-field=score]')[0].value === '0.5-1', 'legacy score filter restored');
        input('.table-date-range[data-field=upload-date] input:first-child', '2026-11-01', 'change');
        input('.table-date-range[data-field=upload-date] input:last-child', '2026-11-07', 'change');
        await wait(() => new URLSearchParams(page.location.search).get('filter_upload-date') === '01.11.2026-07.11.2026', 'native date range');
        button('CSV').click();
        await wait(() => !button('CSV').disabled, 'CSV download finished');
        const requests = await (await fetch('/test/requests')).json();
        const csv = requests.find(item => item.path === '/get_csv/');
        assert(csv && csv.query.latest === '1' && csv.query.filter_user === 'student' && csv.query.filter_score === '0.5-1' && csv.query['filter_upload-date'] === '01.11.2026-07.11.2026', 'export uses active filters');
        await load('/users/student');
        assert(elements('#one-user-table').length === 1 && elements('#user-list-table').length === 0, 'user card shows checks');
        assert(new URLSearchParams(page.location.search).get('filter_user') === 'student', 'user card fixed scope');
        await load('/admin/criterions');
        assert(elements('tbody tr[data-index]').length === 2, 'catalog rows');
        button('Фильтры').click();
        input('.table-filters select[data-field=type]', 'report', 'change');
        await wait(() => elements('tbody tr[data-index]').length === 1, 'local type filter');
        elements('a.detail-icon')[0].click();
        assert(elements('.detail-view')[0].textContent.includes('Описание отчёта'), 'catalog description');
        await load('/criterion_packs/');
        assert(elements('tbody tr[data-index] a')[0].textContent === 'Открыть', 'pack edit link preserved');
        await load('/logs/');
        elements('a.detail-icon')[0].click();
        assert(elements('.detail-view img').length === 0 && elements('.detail-view')[0].textContent.includes('<img'), 'log details escaped');
        await load('/results/test');
        elements('a.detail-icon')[0].click();
        assert(elements('.detail-view b')[0].textContent === 'Замечание', 'result HTML details preserved');
        report.textContent = `ALL TABLE CHECKS PASSED\n${checks.join('\n')}`;
    } catch (error) { report.textContent = `FAILED: ${error.stack}\n${checks.join('\n')}`; }
})();
