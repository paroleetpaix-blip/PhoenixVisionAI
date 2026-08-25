(() => {
    "use strict";


    const $ = id =>
        document.getElementById(id);


    const username =
        document.body.dataset.username;


    function value(
        id,
        content
    ) {
        const element = $(
            id
        );

        if (!element) {
            return;
        }

        element.textContent =
            content ||
            "—";
    }


    function formatDate(
        raw
    ) {
        if (!raw) {
            return "—";
        }

        const date =
            new Date(
                raw
            );

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return raw;
        }

        return (
            new Intl.DateTimeFormat(
                "fr-FR",
                {
                    dateStyle:
                        "medium",

                    timeStyle:
                        "short",
                }
            )
            .format(
                date
            )
        );
    }


    async function requestJson(
        url
    ) {
        const response =
            await fetch(
                url,
                {
                    credentials:
                        "same-origin",
                }
            );


        if (
            response.status ===
            401
        ) {
            window.location.href =
                "/login";

            throw new Error(
                "Session expirée."
            );
        }


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                data.message ||
                data.error ||
                "Erreur Phoenix"
            );
        }


        return data;
    }


    function displayName(
        user
    ) {
        return (
            user.display_name
            ||
            [
                user.prenom,
                user.postnom,
                user.nom,
            ]
            .filter(Boolean)
            .join(" ")
            ||
            user.username
        );
    }


    async function boot() {
        try {

            const data =
                await requestJson(
                    `/api/users/${encodeURIComponent(username)}`
                );


            const user =
                data.user || {};


            const permissions =
                Array.isArray(
                    data.effective_permissions
                )
                ?
                    data.effective_permissions
                :
                    [];


            value(
                "sheet-user-id",
                user.user_id
            );

            value(
                "sheet-footer-id",
                user.user_id
            );

            value(
                "sheet-name",
                displayName(
                    user
                )
            );

            value(
                "sheet-username",
                user.username
            );

            value(
                "sheet-role",
                user.role
            );

            value(
                "sheet-status",
                user.status
            );


            const photo =
                $("sheet-photo");


            if (
                user.photo_url
            ) {
                photo.src =
                    user.photo_url;
            }


            const qr =
                $("sheet-qr");

            qr.src =
                `/api/users/${encodeURIComponent(username)}/qr.svg`;


            value(
                "sheet-last-name",
                user.nom
            );

            value(
                "sheet-middle-name",
                user.postnom
            );

            value(
                "sheet-first-name",
                user.prenom
            );

            value(
                "sheet-matricule",
                user.matricule
            );

            value(
                "sheet-organisation",
                user.organisation
            );

            value(
                "sheet-department",
                user.departement
            );

            value(
                "sheet-job",
                user.fonction
            );

            value(
                "sheet-site",
                user.site_affectation
            );

            value(
                "sheet-manager",
                user.responsable
            );


            const emailField =
                $("sheet-email")
                .closest(
                    ".sensitive-field"
                );

            const phoneField =
                $("sheet-phone")
                .closest(
                    ".sensitive-field"
                );


            if (
                Object.prototype
                .hasOwnProperty
                .call(
                    user,
                    "email"
                )
            ) {
                value(
                    "sheet-email",
                    user.email
                );

            } else {

                emailField.remove();
            }


            if (
                Object.prototype
                .hasOwnProperty
                .call(
                    user,
                    "telephone"
                )
            ) {
                value(
                    "sheet-phone",
                    user.telephone
                );

            } else {

                phoneField.remove();
            }


            value(
                "sheet-login",
                user.username
            );

            value(
                "sheet-role-text",
                user.role
            );

            value(
                "sheet-status-text",
                user.status
            );

            value(
                "sheet-approved-at",
                formatDate(
                    user.approved_at
                )
            );

            value(
                "sheet-approved-by",
                user.approved_by
            );

            value(
                "sheet-expiry",
                user.account_expiry
            );

            value(
                "sheet-last-login",
                formatDate(
                    user.last_login_at
                )
            );

            value(
                "sheet-revision",
                String(
                    user.revision
                    ||
                    "—"
                )
            );


            const container =
                $("sheet-permissions");


            if (
                permissions.length
            ) {

                container.innerHTML =
                    permissions.map(
                        item => {

                            const div =
                                document.createElement(
                                    "div"
                                );

                            div.className =
                                "sheet-permission";

                            div.textContent =
                                item.label;

                            return (
                                div.outerHTML
                            );
                        }
                    ).join("");

            } else {

                container.textContent =
                    "Aucun droit effectif catalogué.";
            }


            value(
                "sheet-generated-at",
                new Intl.DateTimeFormat(
                    "fr-FR",
                    {
                        dateStyle:
                            "medium",

                        timeStyle:
                            "short",
                    }
                )
                .format(
                    new Date()
                )
            );


            $("user-sheet")
                .classList.remove(
                    "loading"
                );


        } catch (error) {

            $("user-sheet")
                .classList.add(
                    "hidden"
                );

            $("sheet-error")
                .classList.remove(
                    "hidden"
                );

            $("sheet-error")
                .textContent =
                    error.message;
        }
    }


    $("print-user-sheet")
        .addEventListener(
            "click",
            () => {
                window.print();
            }
        );


    $("close-user-sheet")
        .addEventListener(
            "click",
            () => {
                window.close();
            }
        );


    document.addEventListener(
        "DOMContentLoaded",
        boot
    );

})();
