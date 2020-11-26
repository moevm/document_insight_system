function save() {
    const post_data = {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: $("#name_text_field").val() })
    };
    fetch("/user", post_data).then(() => { window.location.href = "/profile"; });
}

function logout() {
    const post_data = { method: "GET" };
    fetch("/user", post_data).then(() => { window.location.href = "/login"; });
}

function signout() {
    const post_data = { method: "DELETE" };
    fetch("/user", post_data).then(() => { window.location.href = "/signup"; });
}
