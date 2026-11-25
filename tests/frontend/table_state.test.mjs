import test from 'node:test';
import assert from 'node:assert/strict';
import { readTableState, tableQuery, tableUrl, dateRangeInputs, dateRangeFilter } from '../../assets/scripts/table_state.mjs';
const defaults = { limit: 25, sort: 'username', order: 'asc' };

test('restores JSON filters, page size, sorting and search with literal URL characters', () => {
    const query = new URLSearchParams({ filter: JSON.stringify({ name: 'Иван + 100%', role: 'admin' }), limit: '50', offset: '100', sort: 'name', order: 'desc', search: 'C++' });
    const state = readTableState(`?${query}`, defaults, ['name', 'role']);
    assert.deepEqual(state, { filters: { name: 'Иван + 100%', role: 'admin' }, limit: 50, offset: 100, sort: 'name', order: 'desc', search: 'C++', latest: false });
});

test('prefix links and latest mode round trip without losing filters', () => {
    const initial = '?filter_user=student&filter_score=0.5-1&latest=true&size=10&page=3';
    const state = readTableState(initial, defaults, ['user', 'score']);
    const query = tableQuery(state, 'prefix');
    assert.equal(query.offset, 20);
    assert.equal(query.filter_user, 'student');
    assert.equal(query.filter_score, '0.5-1');
    assert.equal(query.latest, '1');
    assert.deepEqual(readTableState(tableUrl(initial, state, 'prefix'), defaults, ['user', 'score']), state);
});

test('malformed filters and pagination use safe defaults', () => {
    for (const filter of ['{', '[]', 'null', '"text"']) {
        const state = readTableState(`?filter=${encodeURIComponent(filter)}&limit=All&offset=-10&order=bad`, defaults, ['name']);
        assert.deepEqual(state.filters, {});
        assert.equal(state.limit, 25);
        assert.equal(state.offset, 0);
        assert.equal(state.order, 'asc');
    }
});

test('only declared string filters survive; reset removes old links and latest', () => {
    const state = readTableState('?filter=%7B%22name%22%3A3%2C%22unknown%22%3A%22x%22%7D', defaults, ['name']);
    assert.deepEqual(state.filters, {});
    const url = tableUrl('?filter_user=other&latest=1&filter=%7B%7D&other=keep', state, 'prefix');
    const params = new URLSearchParams(url);
    assert.equal(params.get('other'), 'keep');
    assert.equal(params.has('latest'), false);
    assert.equal(params.has('filter_user'), false);
    assert.equal(params.has('filter'), false);
});

test('date controls round trip inclusive dates and either endpoint', () => {
    assert.deepEqual(dateRangeInputs('01.11.2026-07.11.2026'), ['2026-11-01', '2026-11-07']);
    assert.deepEqual(dateRangeInputs('07.11.2026'), ['2026-11-07', '']);
    assert.equal(dateRangeFilter('2026-11-01', '2026-11-07'), '01.11.2026-07.11.2026');
    assert.equal(dateRangeFilter('', '2026-11-07'), '07.11.2026');
    assert.equal(dateRangeFilter('', ''), '');
});
