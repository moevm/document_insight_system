import { DataTable } from './data_table';

$(() => new DataTable('#results_table', {
    sort: 'id', details: row => row._detail || 'Описание отсутствует.',
    filters: [
        { field: 'id', label: 'ID критерия' }, { field: 'label', label: 'Название' },
        { field: 'type', label: 'Тип', values: [['report', 'Отчёт'], ['pres', 'Презентация']] }
    ]
}));
