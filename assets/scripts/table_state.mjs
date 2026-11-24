export function readTableState(search, defaults, fields) {
    const query = new URLSearchParams(search);
    let filters = {};
    try {
        const parsed = JSON.parse(query.get('filter') || '{}');
        if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) filters = parsed;
    } catch (_) { /* Ignore malformed links and keep the table usable. */ }
    for (const field of fields) {
        if (query.has(`filter_${field}`)) filters[field] = query.get(`filter_${field}`);
    }
    filters = Object.fromEntries(fields.filter(field => typeof filters[field] === 'string' && filters[field])
        .map(field => [field, filters[field]]));
    const size = Number(query.get('limit') || query.get('size'));
    const limit = [10, 25, 50, 100].includes(size) ? size : defaults.limit;
    const offset = Number(query.get('offset') || (Number(query.get('page') || 1) - 1) * limit);
    return {
        filters, limit, offset: Number.isSafeInteger(offset) && offset >= 0 ? offset : 0,
        sort: query.get('sort') || defaults.sort,
        order: ['asc', 'desc'].includes(query.get('order')) ? query.get('order') : defaults.order,
        search: query.get('search') || '', latest: ['1', 'true'].includes(query.get('latest'))
    };
}

export function tableQuery(state, mode = 'json') {
    const query = { limit: state.limit, offset: state.offset, sort: state.sort, order: state.order };
    if (state.search) query.search = state.search;
    if (state.latest) query.latest = '1';
    if (mode === 'prefix') {
        for (const [key, value] of Object.entries(state.filters)) if (value) query[`filter_${key}`] = value;
    } else if (Object.keys(state.filters).length) query.filter = JSON.stringify(state.filters);
    return query;
}

export function tableUrl(search, state, mode) {
    const query = new URLSearchParams(search);
    for (const key of [...query.keys()]) {
        if (key.startsWith('filter_') || ['filter', 'limit', 'offset', 'sort', 'order', 'page', 'size', 'search', 'latest'].includes(key)) query.delete(key);
    }
    for (const [key, value] of Object.entries(tableQuery(state, mode))) query.set(key, value);
    return `?${query}`;
}

const russianDate = value => value.split('-').reverse().join('.');

export function dateRangeInputs(value = '') {
    const sides = String(value).replace(/\u2013/g, '-').split('-');
    const parse = text => {
        const date = /(\d{1,2})\.(\d{1,2})\.(\d{4})/.exec(text || '');
        const time = /(\d{1,2}):(\d{2})/.exec(text || '');
        return [
            date ? `${date[3]}-${date[2].padStart(2, '0')}-${date[1].padStart(2, '0')}` : '',
            time ? `${time[1].padStart(2, '0')}:${time[2]}` : ''
        ];
    };
    const start = parse(sides[0]);
    const end = parse(sides[1]);
    if (!end[0] && end[1]) end[0] = start[0];
    return [start, end];
}

export function dateRangeFilter(sides = []) {
    const [[startDate, startTime] = [], [rawEndDate, endTime] = []] = sides;
    // a time without its own date belongs to the start day: "24.11.2026 12:00-15:00"
    const endDate = rawEndDate || (endTime ? startDate : '');
    const russian = (date, time) => `${russianDate(date)}${time ? ` ${time}` : ''}`;
    if (!startDate) return endDate ? russian(endDate, endTime) : '';
    if (!endDate) return russian(startDate, startTime);
    // the upper end is exclusive: a same-day end keeps its own day unless the start covers the whole day
    const start = russian(startDate, startDate === endDate && !startTime ? '' : startTime);
    if (startDate === endDate && !startTime && !endTime) return start;
    const end = endDate === startDate ? endTime || russian(endDate, '') : russian(endDate, endTime);
    return `${start}-${end}`;
}
