import * as md5 from "md5";

export function hash(password) {
	return md5(password)
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
