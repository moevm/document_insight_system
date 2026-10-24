export function debounce(func, timeout) {
    let lastCallTimer = null;
    let lastCallArgs = [];

    return function perform(...args) {
        lastCallArgs = args;
        clearTimeout(lastCallTimer);
        lastCallTimer = setTimeout(() => func(...lastCallArgs), timeout);
    }
};

export function isFloat(str) {
    const floatRegex = /^-?\d+(?:[.,]\d*?)?$/;
    if (!floatRegex.test(str))
        return false;

    str = parseFloat(str);
    if (isNaN(str))
        return false;
    return true;
};


export function pushHistoryState(paramsData) {
    const query = {};
    for (const [key, value] of Object.entries(paramsData)) {
        if (value === undefined || value === null || value === "") {
            continue;
        }
        query[key] = value;
    }

    history.pushState(paramsData, "", "?" + $.param(query))
};


export function ajaxRequest(AJAX_URL, params) {
    const queryString = "?" + $.param(params.data)
    const url = AJAX_URL + queryString
    console.log("ajax:", url);
    $.get(url).then(res => params.success(res))

    pushHistoryState(params.data)
};


export function onPopState() {
    location.reload()
};


export function resetTable($table, queryParams) {
    let queryString = window.location.search;
    const params = Object.fromEntries(new URLSearchParams(decodeURIComponent(queryString)).entries());

    for (const key of Object.keys(params)) {
        if (key === "filter" || key.startsWith("filter_")) {
            delete params[key];
        }
    }

    $(".filter-control input").each(function () {
        if (this._flatpickr) {
            this._flatpickr.clear();
        }
        $(this).val("");
    });

    pushHistoryState(params);

    $table.bootstrapTable('refreshOptions', {
        sortName: "",
        sortOrder: "",
        queryParams: queryParams
    });
}