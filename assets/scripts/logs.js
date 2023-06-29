import { debounce, isFloat, resetTable, ajaxRequest, onPopState } from "./utils"

let $table;
const AJAX_URL = "/logs/data"
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


function initTable() {
    $table = $("#logs-table");

    // get query string
    const queryString = window.location.search;

    // parse query search to js object
    const params = Object.fromEntries(new URLSearchParams(queryString).entries())

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
            params.filter = JSON.parse(decodeURI(params.filter))
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
        detailView: true,
        detailViewIcon: false,
        detailViewByClick: true,
        detailFormatter: detailFormatter,

        queryParams: queryParams,
        ajax: debouncedAjaxRequest
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
    }

    if (!$.isEmptyObject(filters)) {
        query.filter = JSON.stringify(filters)
    }

    return query
}


function buttons() {
    let buttonsObj = {}

    buttonsObj["ResetTable"] = {
        text: 'Reset',
        event: function() { resetTable($table, queryParams) }
    }

    return buttonsObj
}


function detailFormatter(index, row) {
    var html = []
    $.each(row, function (key, value) {
        if (key === 'message' || key === 'pathname') {
            html.push('<p><b>' + key + ':</b> ' + row[key] + '</p>')
        }
    })
    return html.join('')
}
