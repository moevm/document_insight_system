import "../styles/version.css";

$(() => {
    $("pre.line-numbers").each(function () {
        const text = this.innerHTML;
        this.innerHTML = "";
        text.split(/\r?\n/).forEach(line => {
            $(`<code>${line}</code>`).appendTo(this);
        });
    })
})
