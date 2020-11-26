$('.caret').click(function () {
    console.log(this);
    $(this).parent().find('.nested').toggleClass("active");
    $(this).toggleClass("caret-down");
});
