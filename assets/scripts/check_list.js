import { debounce, isFloat, resetTable, ajaxRequest, onPopState } from "./utils"

let $table;
const AJAX_URL = "/check_list/data";
const filter_prefix = 'filter_';
let is_latest = false;
let debounceInterval = 500;


String.prototype.insert = function (index, string) {
    if (index > 0) {
        return this.substring(0, index) + string + this.substr(index)
    }
    return string + this
}


$(() => {
    initTable()
    window.onpopstate = onPopState

    const $dataFilter = $(".bootstrap-table-filter-control-result")
    $dataFilter.on("keypress", (e) => {
        const val = $dataFilter.val()
        const numbers = val.split("-")

        if (e.key === ".") {
            const carret = $dataFilter[0].selectionStart
            let expectedStr
            if (carret <= numbers[0].length) {
                expectedStr = numbers[0].insert(carret, ".")
            } else {
                expectedStr = numbers[1].insert(carret - numbers[0].length - 1, ".")
            }

            if (isFloat(expectedStr)) {
                return
            }
        }

        if (e.key >= "0" && e.key <= "9") {
            return
        }

        if (e.key === "-") {
            if (numbers.length === 1) {
                return
            }
        }

        e.preventDefault()
    })
})


function extract_filters(params){
    var filters = {}
    for (const [key, value] of Object.entries(params)) {
        const index = key.indexOf(filter_prefix) !== -1
        if (index !== -1) {
            filters[key.substring(filter_prefix.length)] = value
        }
    }
    return filters
}


function initTable() {
    $table = $("#check-list-table");

    // get query string
    const queryString = window.location.search;
    console.log(queryString)
    // parse query search to js object
    const params = Object.fromEntries(new URLSearchParams(decodeURIComponent(queryString)).entries())
    // configure filter
    params.filter = extract_filters(params)
    console.log(params)

    // check correct order query
    if (params.order !== "asc" && params.order !== "desc" && params.order !== "") {
        params.order = ""
    }

    // check correct sort query
    if (params.sort !== "") {
        let match = false
        $table.find("th[data-sortable='true']").each(function () {
            if ($(this).data("field") === params.sort) {
                match = true
                return false
            }
        })

        if (match === false) {
            params.sort = ""
        }
    }


    // check pair of sort and order
    if ([params.sort, params.order].includes("")) {
        params.sort = ""
        params.order = ""
    }

    // Fill filters
    $table.on("created-controls.bs.table", function () {
        if (params.filter) {
            console.log(params.filter)
            for (const [key, value] of Object.entries(params.filter)) {
                const $input = $(`.bootstrap-table-filter-control-${key}`)
                $input.val(value)
            }
        }
    })

    // activate bs table
    $table.bootstrapTable({
        pageNumber: parseInt(params.page) || 1,
        pageSize: parseInt(params.size) || 10,
        sortName: params.sort,
        sortOrder: params.order,
        buttons: buttons,

        queryParams: queryParams,
        ajax: debouncedAjaxRequest,

        columns: [{
            field: "_id",
            formatter: idFormatter
        }]
    })
}


// debounced ajax calls.
const debouncedAjaxRequest = debounce(function(params) {ajaxRequest(AJAX_URL, params)}, debounceInterval);


function queryParams(params) {
    let filters = {}
    $('.filter-control').each(function () {
        const name = $(this).parents("th").data("field")
        const val = this.querySelector("input").value
        if (val) {
            filters[name] = val
        }
    })

    const query = {
        limit: params.limit,
        offset: params.offset,
        sort: params.sort,
        order: params.order,
        latest: params.latest
    }

    if (!$.isEmptyObject(filters)) {
        for (const [key, value] of Object.entries(filters)){
            query[`${filter_prefix}${key}`] = value
        }
    }

    return query
}


function idFormatter(value, row, index, field) {
    return `<a href="/results/${value}">${value.slice(0, 5)}-${value.slice(-5)}</a>`
}


function timeStamp() {
    var now = new Date();
    var date = [now.getMonth() + 1, now.getDate(), now.getFullYear()];
    var time = [now.getHours(), now.getMinutes(), now.getSeconds()];
    var suffix = (time[0] < 12) ? "AM" : "PM";

    time[0] = (time[0] < 12) ? time[0] : time[0] - 12;
    time[0] = time[0] || 12;
    for (var i = 1; i < 3; i++) {
        if (time[i] < 10) {
            time[i] = "0" + time[i];
        }
    }
    return '[' + date.join(".") + "_" + time.join(".") + suffix + ']';
}


function buttons() {
    let buttonsObj = {};

    buttonsObj["ResetTable"] = {
        text: 'Reset',
        event: function() { resetTable($table, queryParams) }
    };

    if (is_admin) {
        buttonsObj["FetchCSV"] = {
            text: 'CSV',
            event: function () {
                //const queryString = window.location.search
                const params = window.location.search
                $("[name=FetchCSV]")[0].innerHTML = "<span class='spinner-border spinner-border-sm'></span>   Exporting..."
                fetch('get_csv' + '?' + params)
                    .then(response => response.blob())
                    .then(blob => {
                        $("[name=FetchCSV]")[0].textContent = "CSV"
                        downdloadBlob(blob, `Статистика.csv`)
                    });
            }
        };

        buttonsObj["FetchZip"] = {
            text: 'Скачать архив',
            event: function () {
                const params = window.location.search
                $("[name=FetchZip]")[0].innerHTML = "<span class='spinner-border spinner-border-sm'></span>   Архивирование..."
                fetch('get_zip' + '?' + params)
                    .then(response => response.ok ? response.blob() : false)
                    .then(blob => {
                        $("[name=FetchZip]")[0].textContent = "Скачать архив"
                        if (blob)
                            downdloadBlob(blob, `Статистика_и_файлы.zip`)
                        else
                            alert("Error during file download")
                    });
            }
        };

        buttonsObj["LatestChecks"] = {
            text: 'Latest',
            event: function () {
                is_latest = !is_latest;
                let query = {}
                if (is_latest === true){
                    query = { query: { latest: is_latest } }
                }
                $("#check-list-table").bootstrapTable('refresh', query);
            }
        };
    }
    return buttonsObj;
}


function downdloadBlob(blob, filename) {
    var url = window.URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
}