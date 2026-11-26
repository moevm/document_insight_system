import '../styles/data_table.css';
import 'bootstrap-table/dist/locale/bootstrap-table-ru-RU';
import { readTableState, tableQuery, tableUrl, dateRangeInputs, dateRangeFilter } from './table_state.mjs';

export const escapeHtml = value => $('<span>').text(value == null ? '' : String(value)).html();
export const link = (path, value, label = value) => `<a class="table-link" href="${path}${encodeURIComponent(value)}" title="${escapeHtml(label)}">${escapeHtml(label)}</a>`;
export const badge = (text, kind = 'secondary') => `<span class="badge badge-${kind}">${escapeHtml(text)}</span>`;
const plainText = value => $('<div>').html(value == null ? '' : String(value)).text();

export class DataTable {
    constructor(selector, options = {}) {
        this.$table = $(selector);
        if (!this.$table.length) return;
        this.options = options;
        this.filters = options.filters || [];
        this.defaults = { limit: 25, sort: options.sort || '', order: options.order || 'asc' };
        this.state = readTableState(location.search, this.defaults, this.filters.map(field => field.field));
        Object.assign(this.state.filters, options.fixedFilters || {});
        const sortable = this.$table.find('th[data-sortable="true"]').map((_, th) => $(th).data('field')).get();
        if (!sortable.includes(this.state.sort)) this.state.sort = this.defaults.sort;
        this.$shell = $('<section class="data-table-panel">');
        this.$table.wrap(this.$shell);
        this.$shell = this.$table.parent();
        this.createToolbar();
        this.$error = $('<div class="alert alert-danger table-error" role="alert" hidden>Не удалось загрузить данные. Нажмите «Обновить», чтобы повторить.</div>').prependTo(this.$shell);
        this.rows = options.url ? null : this.readRows();
        this.$table.addClass('table table-hover data-table').bootstrapTable({
            locale: 'ru-RU', iconsPrefix: 'bi', icons: { detailOpen: 'bi-plus-square', detailClose: 'bi-dash-square' }, pagination: true, sidePagination: options.url ? 'server' : 'client',
            pageList: [10, 25, 50, 100], pageSize: this.state.limit,
            pageNumber: Math.floor(this.state.offset / this.state.limit) + 1,
            sortName: this.state.sort, sortOrder: this.state.order,
            showColumns: true, showColumnsToggleAll: true, minimumCountColumns: 1,
            escape: false, undefinedText: '—', search: false, classes: 'table table-hover',
            searchTimeOut: 350, columns: this.$table.find('thead th').map((_, th) => {
                const field = $(th).data('field');
                const column = (options.columns || []).find(item => item.field === field) || {};
                return { field, escape: !column.formatter && !$(th).is('[data-html]'), ...column };
            }).get(),
            data: this.rows ? this.filteredRows() : undefined,
            detailView: !!options.details,
            detailFormatter: (_, row) => options.details(row),
            ajax: options.url ? params => this.request(params) : undefined,
            queryParams: params => {
                Object.assign(this.state, { limit: params.limit, offset: params.offset, sort: params.sort || this.defaults.sort, order: params.order });
                return tableQuery(this.state, options.filterMode);
            },
            onPageChange: (page, size) => {
                this.state.limit = size;
                this.state.offset = (page - 1) * size;
                this.writeUrl();
            },
            onSort: (sort, order) => { Object.assign(this.state, { sort, order, offset: 0 }); this.writeUrl(); }
        });
        this.$table.on('post-body.bs.table', () => this.labelControls());
        this.labelControls();
        this.writeUrl(true);
        window.addEventListener('popstate', () => location.reload());
        if (options.refresh) this.startAutoRefresh();
    }

    createToolbar() {
        const $toolbar = $('<div class="data-table-toolbar">').prependTo(this.$shell);
        const $search = $('<input type="search" class="form-control table-search" aria-label="Поиск по таблице" placeholder="Поиск…">')
            .val(this.state.search).appendTo($toolbar);
        const $actions = this.$actions = $('<div class="table-actions">').appendTo($toolbar);
        this.button($actions, 'Фильтры', () => {
            const expanded = this.$filters.prop('hidden');
            this.$filters.prop('hidden', !expanded);
            this.$filterButton.attr('aria-expanded', String(expanded));
        });
        this.$filterButton = $actions.children().last().attr({ 'aria-expanded': String(Object.keys(this.state.filters).length > 0), 'aria-controls': `${this.$table.attr('id')}-filters` });
        this.button($actions, 'Сбросить', () => {
            clearTimeout(this.timer);
            this.timer = null;
            this.state = { ...this.defaults, limit: this.state.limit, offset: 0, search: '', latest: false, filters: {} };
            $search.val('');
            this.$filters.find('input, select').val('');
            this.$shell.find('[data-latest]').attr('aria-pressed', 'false');
            this.applyFilters();
        });
        if (this.options.url) this.button($actions, 'Обновить', () => this.refresh());
        if (this.options.refresh) {
            $('<label class="table-auto-refresh"><input type="checkbox"> Автообновление</label>').appendTo($actions)
                .find('input').on('change', event => { this.autoRefresh = event.target.checked; });
        }
        if (this.options.latest) this.button($actions, 'Последние проверки', event => {
            this.state.latest = !this.state.latest;
            $(event.currentTarget).attr('aria-pressed', String(this.state.latest));
            this.applyFilters();
        }).attr({ 'data-latest': '', 'aria-pressed': String(this.state.latest) });
        for (const action of this.options.actions || []) this.button($actions, action.label, event => this.download(action, event.currentTarget));
        if (this.options.details) {
            this.button($actions, 'Раскрыть строки', () => this.$table.bootstrapTable('expandAllRows'));
            this.button($actions, 'Свернуть строки', () => this.$table.bootstrapTable('collapseAllRows'));
        }
        this.$filters = $('<div class="table-filters">').attr('id', `${this.$table.attr('id')}-filters`)
            .prop('hidden', !Object.keys(this.state.filters).length).insertBefore(this.$table);
        for (const field of this.filters) {
            if (field.type === 'date-range') {
                const $group = $('<fieldset class="table-filter">').appendTo(this.$filters);
                $('<legend>').text(field.label).appendTo($group);
                const $range = $('<div class="table-date-range">').attr('data-field', field.field).appendTo($group);
                const values = dateRangeInputs(this.state.filters[field.field]);
                ['с', 'по'].forEach((label, index) => {
                    $('<input type="date" class="form-control">').attr('aria-label', `${field.label}: ${label}`)
                        .val(values[index]).appendTo($range).on('change', () => this.scheduleFilters());
                });
                continue;
            }
            const $label = $('<label class="table-filter">').text(field.label).appendTo(this.$filters);
            const $input = field.values ? $('<select class="form-control"><option value="">Все</option></select>') : $('<input type="text" class="form-control">');
            for (const [value, label] of field.values || []) $('<option>').val(value).text(label).appendTo($input);
            $input.attr({ 'data-field': field.field, placeholder: field.placeholder || 'Содержит…', 'aria-label': field.label })
                .val(this.state.filters[field.field] || '').appendTo($label).on(field.values ? 'change' : 'input', () => this.scheduleFilters());
            if (field.hint) $('<small class="text-muted">').text(field.hint).appendTo($label);
        }
        if (!this.filters.length) this.$filterButton.hide();
        $search.on('input', () => { this.state.search = $search.val().trim(); this.scheduleFilters(); });
    }

    button($parent, label, action) {
        return $('<button type="button" class="btn btn-sm btn-outline-secondary">').text(label).on('click', action).appendTo($parent);
    }

    scheduleFilters() {
        clearTimeout(this.timer);
        this.timer = setTimeout(() => {
            this.timer = null;
            this.state.filters = {};
            this.$filters.find('[data-field]').each((_, input) => {
                const value = $(input).hasClass('table-date-range')
                    ? dateRangeFilter(...$(input).find('input').map((_, date) => date.value).get())
                    : $(input).val().trim();
                if (value) this.state.filters[$(input).data('field')] = value;
            });
            this.applyFilters();
        }, 350);
    }

    applyFilters() {
        Object.assign(this.state.filters, this.options.fixedFilters || {});
        this.state.offset = 0;
        this.writeUrl();
        if (this.options.url) {
            this.$table.bootstrapTable('refreshOptions', { pageNumber: 1, sortName: this.state.sort, sortOrder: this.state.order });
        } else {
            this.$table.bootstrapTable('refreshOptions', { data: this.filteredRows(), pageNumber: 1, sortName: this.state.sort, sortOrder: this.state.order });
        }
    }

    filteredRows() {
        return this.rows.filter(row => {
            const search = this.state.search.toLocaleLowerCase('ru');
            const text = Object.values(row).map(plainText).join(' ').toLocaleLowerCase('ru');
            return text.includes(search) && this.filters.every(field => {
                const filter = this.state.filters[field.field];
                const value = plainText(row[field.field]);
                return !filter || (field.values ? value === filter : value.toLocaleLowerCase('ru').includes(filter.toLocaleLowerCase('ru')));
            });
        });
    }

    readRows() {
        const fields = this.$table.find('thead th').map((_, th) => $(th).data('field')).get();
        const rows = [];
        this.$table.find('tbody > tr').each((_, tr) => {
            if ($(tr).is('[data-detail]')) {
                if (rows.length) rows[rows.length - 1]._detail = $(tr).find('td').html();
                return;
            }
            const row = {};
            $(tr).children('td, th').each((index, cell) => {
                row[fields[index]] = this.$table.find(`thead th[data-field="${fields[index]}"]`).is('[data-html]') ? $(cell).html() : $(cell).text().trim();
            });
            rows.push(row);
        });
        this.$table.find('tbody').empty();
        return rows;
    }

    request(params) {
        if (this.pending) this.pending.abort();
        this.writeUrl();
        this.$error.text('Не удалось загрузить данные. Нажмите «Обновить», чтобы повторить.').prop('hidden', true);
        this.$table.attr('aria-busy', 'true');
        const request = $.ajax({ url: this.options.url, data: params.data, dataType: 'json' });
        this.pending = request;
        request.done(data => {
                if (!Array.isArray(data.rows) || !Number.isFinite(data.total)) {
                    this.$error.prop('hidden', false);
                    params.error();
                    return;
                }
                if (data.total > 0 && this.state.offset >= data.total) {
                    this.state.offset = Math.floor((data.total - 1) / this.state.limit) * this.state.limit;
                    this.$table.bootstrapTable('selectPage', this.state.offset / this.state.limit + 1);
                    return;
                }
                params.success(data);
            })
            .fail((response, status) => {
                if (status !== 'abort') { this.$error.text(response.responseJSON?.error || 'Не удалось загрузить данные. Нажмите «Обновить», чтобы повторить.').prop('hidden', false); params.error(); }
            })
            .always(() => {
                if (this.pending === request) { this.pending = null; this.$table.attr('aria-busy', 'false'); }
            });
    }

    refresh() {
        if (!this.pending || this.pending.readyState === 4) this.$table.bootstrapTable('refresh', { silent: true });
    }

    startAutoRefresh() {
        const timer = setInterval(() => {
            if (this.autoRefresh && !document.hidden && !this.$shell.find(':focus').length && !this.timer) this.refresh();
        }, 10000);
        window.addEventListener('pagehide', () => clearInterval(timer), { once: true });
    }

    writeUrl(replace = false) {
        const url = tableUrl(location.search, this.state, this.options.filterMode);
        if (url !== location.search) history[replace ? 'replaceState' : 'pushState'](null, '', url);
    }

    labelControls() {
        const $toolbar = this.$table.closest('.bootstrap-table').find('.fixed-table-toolbar');
        if ($toolbar.length) {
            this.$actions.children('.fixed-table-toolbar').remove();
            $toolbar.appendTo(this.$actions);
        }
        this.$actions.find('.keep-open button').text('Столбцы').attr('aria-label', 'Выбрать столбцы')
            .removeClass('btn-secondary').addClass('btn-sm btn-outline-secondary');
        this.$shell.find('th[data-sortable="true"]').attr('tabindex', '0').off('keydown.data-table').on('keydown.data-table', event => {
            if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); $(event.currentTarget).find('.th-inner').trigger('click'); }
        });
    }

    async download(action, button) {
        $(button).prop('disabled', true);
        this.$error.prop('hidden', true);
        try {
            const query = new URLSearchParams(tableQuery(this.state, this.options.filterMode));
            const response = await fetch(`${action.url}?${query}`);
            if (!response.ok) throw new Error('download failed');
            const url = URL.createObjectURL(await response.blob());
            const a = document.createElement('a');
            a.href = url;
            a.download = action.filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (_) {
            this.$error.text('Не удалось скачать файл. Повторите попытку.').prop('hidden', false);
        } finally { $(button).prop('disabled', false); }
    }
}
