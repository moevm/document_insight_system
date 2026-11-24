import { DataTable, escapeHtml, badge } from './data_table';

$(() => new DataTable('#logs-table', {
    url: '/logs/data', sort: 'timestamp', order: 'desc', refresh: true,
    filters: [
        { field: 'timestamp', type: 'date-range', label: 'Дата', hint: 'Без времени — вся дата; с временем «по» — до указанной минуты, не включая её.' },
        { field: 'check_id', label: 'ID проверки' }, { field: 'stage', label: 'Этап' },
        { field: 'service-name', label: 'Сервис' },
        { field: 'levelname', label: 'Уровень', values: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].map(level => [level, level]) },
        { field: 'pathname', label: 'Путь' }, { field: 'lineno', label: 'Строка', placeholder: '10 или 10-50' }
    ],
    details: row => `<pre>${escapeHtml(row.message)}\n${escapeHtml(row.pathname)}</pre>`,
    columns: [{ field: 'levelname', formatter: value => badge(value, ['ERROR', 'CRITICAL'].includes(value) ? 'danger' : value === 'WARNING' ? 'warning' : 'secondary') }]
}));
