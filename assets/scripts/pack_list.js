import { DataTable } from './data_table';
$(() => new DataTable('#pack-list-table', {
    sort: 'name', filters: [
        { field: 'name', label: 'Название набора' },
        { field: 'type', label: 'Тип', values: [['Отчёт. ВКР', 'Отчёт · ВКР'], ['Отчёт. ЛР', 'Отчёт · ЛР'], ['Презентация', 'Презентация']] }
    ], columns: [{ field: 'edit', escape: false }]
}));
