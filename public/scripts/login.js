function login() {
    const params = collect_values_if_possible("login_text_field", "password_text_field");

    if (!params) {
        console.log("Params not collected!");
        return;
    }

    const post_data = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            username: params["login_text_field"],
            password_hash: hash(params["password_text_field"])
        })
    };
    fetch("/login", post_data).then((response) => {
            return response.text();
        }).then((name) => {
            console.log("User " + name + " was" + (name === "" ? " not" : "") + " logged in");
            if (name === "") $("#login_text_field").toggleClass("is-invalid", true);
            else window.location.href = "/upload";
        });
}
