import '../styles/presentations.css';


$('.caret').click(function () {
    $(this).parent().parent().find('.nested').toggleClass("active");
    $(this).toggleClass("caret-down");
});

$('.micro_button').click(async function () {
    const put_data = {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ presentation: this.id })
    };
    await fetch('/upload', put_data);
    $(this).parent().parent().remove();
});
