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

export function dateRangeInputs(value = '') {
    const parts = value.split('-').map(part => part.trim().split('.').reverse().join('-'));
    return [parts[0] || '', parts[1] || ''];
}

export function dateRangeFilter(start, end) {
    if (!start && !end) return '';
    const values = [start || end, end || start].map(value => value.split('-').reverse().join('.'));
    return values[0] === values[1] ? values[0] : values.join('-');
}
