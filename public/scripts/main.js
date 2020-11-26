function hash(password) {
    let hash = 0;
    if (password.length === 0) return hash;
    for (let i = 0; i < password.length; i++) {
        const char = password.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash = hash & hash;
    }
    return hash;
}

function collect_values_if_possible(...ids) {
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
