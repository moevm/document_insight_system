import { mountChecks } from './check_table';

$(() => {
    $("#user-role-form").on("submit", function (event) {
        event.preventDefault();
        const $form = $(this);
        const $button = $form.find("button[type=submit]");
        const $status = $("#user-role-status");
        const isAdmin = $("#user-role").val() === "true";
        $button.prop("disabled", true);
        $status.text("");
        $.ajax({
            url: $form.attr("data-url"),
            method: "PUT",
            contentType: "application/json",
            data: JSON.stringify({ is_admin: isAdmin })
        }).done(() => {
            if ($form.attr("data-is-self") === "true" && !isAdmin) {
                window.location.assign("/");
                return;
            }
            $status.text("Роль сохранена.");
        }).fail((response) => {
            $status.text(response.responseJSON?.error || "Не удалось сохранить роль.");
        }).always(() => {
            $button.prop("disabled", false);
        });
    });
    mountChecks('#one-user-table');
});
