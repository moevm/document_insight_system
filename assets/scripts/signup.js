import {collect_values_if_possible, hash} from "./main";

import '../styles/signup.css';


$("#signup_button").click(async () => {
    const params = collect_values_if_possible("login_text_field", "name_text_field",
        "surname_text_field", "password_text_field", "confirmation_text_field");

    if (!params) {
        console.log("Params not collected!");
        return;
    } else if (params["password_text_field"] !== params["confirmation_text_field"]) {
        $("#confirmation_text_field").toggleClass("is-invalid", true);
        return;
    }

    const post_data = {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            username: params["login_text_field"],
            password_hash: hash(params["password_text_field"]),
            name: params["surname_text_field"] + " " + params["name_text_field"]
        })
    };
    const name = await (await fetch("/signup", post_data)).text();
    console.log("User " + name + " was" + (name === "" ? " not" : "") + " signed up");
    if (name === "") $("#login_text_field").toggleClass("is-invalid", true);
    else window.location.href = "/upload";
});
