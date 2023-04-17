import '../styles/profile.css';


$('#user_save_button').click(async () => {
    const post_data = {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name: $("#name_text_field").val()})
    };
    await fetch("/user", post_data);
    window.location.href = "/profile";
});

$('#user_logout_button').click(async () => {
    const post_data = {method: "GET"};
    await fetch("/user", post_data);
    window.location.href = "/login";
});
