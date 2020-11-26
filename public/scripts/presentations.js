$('.caret').click(function () {
    $(this).parent().parent().find('.nested').toggleClass("active");
    $(this).toggleClass("caret-down");
});

$('.micro_button').click(function () {
    const put_data = {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ presentation: this.id })
    };
    fetch('/upload', put_data).then(() => { $(this).parent().parent().remove(); });
});
