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
    const {limit, offset, sort, order, filter} = paramsData;

    // push history state
    history.pushState(paramsData, "", "?" + $.param({limit, offset, filter, sort, order}))
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
    params.filter = "";

    pushHistoryState(params);

    $table.bootstrapTable('refreshOptions', {
        sortName: "",
        sortOrder: "",
        queryParams: queryParams
    });
}