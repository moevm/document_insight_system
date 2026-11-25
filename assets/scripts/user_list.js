import { DataTable, link, badge } from './data_table';

$(() => new DataTable('#user-list-table', {
    url: '/users/data', sort: 'username', refresh: true,
    filters: [
        { field: 'username', label: 'Логин' }, { field: 'name', label: 'Имя' },
        { field: 'role', label: 'Роль', values: [['admin', 'Администратор'], ['user', 'Пользователь']] },
        { field: 'is_LTI', label: 'Вход', values: [['true', 'LTI'], ['false', 'Локальный']] },
        { field: 'all_formats', label: 'Формат', values: ['docx', 'doc', 'odt', 'md', 'pptx', 'ppt', 'odp'].map(value => [value, value.toUpperCase()]) },
        { field: 'all_criteria', label: 'Набор критериев' },
        { field: 'check_counts', label: 'Число загрузок', placeholder: '>= 5', hint: 'Например: 5, > 5, >= 5, < 10, <= 10' }
    ],
    columns: [
        { field: 'username', formatter: value => link('/users/', value) },
        { field: 'role', formatter: value => badge(value, value === 'Администратор' ? 'primary' : 'secondary') },
        { field: 'is_LTI', formatter: value => badge(value ? 'LTI' : 'Локальный', value ? 'info' : 'secondary') },
        { field: 'all_formats', formatter: value => (value || []).map(format => badge(format.toUpperCase(), 'light')).join(' ') }
    ]
}));
