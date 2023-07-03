import 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

import 'bootstrap-table';
import 'bootstrap-table/dist/bootstrap-table.min.css'

import 'bootstrap-table/dist/extensions/filter-control/bootstrap-table-filter-control'
import 'bootstrap-table/dist/extensions/filter-control/bootstrap-table-filter-control.min.css'

import 'bootstrap-table/dist/extensions/auto-refresh/bootstrap-table-auto-refresh.js'

import 'bootstrap-icons/font/bootstrap-icons.css'

import 'bootstrap-datepicker';
import 'bootstrap-datepicker/dist/css/bootstrap-datepicker.min.css'

import * as CryptoJS from "crypto-js";

import '../styles/main.css';

import './criterion_pack'
import './login';
import './profile';
import './results';
import './signup';
import './upload';
import './version';
import './check_list';
import './logs';

import '../favicon.ico';
import '../styles/404.css';


export function hash(password) {
    return CryptoJS.MD5(password).toString()
}

export function collect_values_if_possible(...ids) {
    const id_array = [...ids];
    const necessary_fields = $(id_array.map(el => "#" + el).join(", "));
    let valid = true;
    necessary_fields.map(function () {
        $(this).toggleClass("is-invalid", this.value === "");
        valid &= (this.value !== "");
        return this;
    });
    if (valid) {
        const result = Object();
        for (const field of necessary_fields) result[field.id] = field.value;
        return result;
    }
}
