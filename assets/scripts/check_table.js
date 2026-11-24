import { DataTable, link, badge } from './data_table';

export function mountChecks(selector) {
    const $table = $(selector);
    if (!$table.length) return;
    const fixedUser = $table.attr('data-user');
    const admin = $table.attr('data-admin') === 'true';
    return new DataTable(selector, {
        url: '/check_list/data', filterMode: 'prefix', sort: 'upload-date', order: 'desc', refresh: true,
        fixedFilters: fixedUser ? { user: fixedUser } : {}, latest: admin,
        filters: [
            { field: 'filename', label: 'Файл' },
            { field: 'criteria', label: 'Набор критериев', hint: 'Несколько названий — через запятую' },
            ...(admin && !fixedUser ? [{ field: 'user', label: 'Пользователь' }] : []),
            { field: 'status', label: 'Состояние', values: [['processing', 'В обработке'], ['failed', 'Ошибка'], ['passed', 'Пройдена'], ['not-passed', 'Не пройдена']] },
            { field: 'score', label: 'Оценка', placeholder: '0.5 или 0.5-1', hint: 'Точное значение или диапазон, от 0 до 1' },
            { field: 'upload-date', type: 'date-range', label: 'Дата загрузки', placeholder: '01.11.2026-07.11.2026', hint: 'ДД.ММ.ГГГГ или диапазон включительно' },
            { field: 'moodle-date', type: 'date-range', label: 'Дата оценки в LMS', placeholder: '01.11.2026-07.11.2026' }
        ],
        actions: admin ? [
            { label: 'CSV', url: '/get_csv/', filename: 'Статистика.csv' },
            { label: 'Скачать архив', url: '/get_zip/', filename: 'Статистика_и_файлы.zip' }
        ] : [],
        columns: [
            { field: '_id', formatter: value => link('/results/', value, `${value.slice(0, 5)}…${value.slice(-5)}`) },
            { field: 'status', formatter: (_, row) => badge(row.status, row.is_failed ? 'danger' : row.is_ended ? row.is_passed ? 'success' : 'warning' : 'info') },
            { field: 'score', formatter: value => value < 0 ? '—' : Number(value).toLocaleString('ru-RU', { maximumFractionDigits: 3 }) }
        ]
    });
}
