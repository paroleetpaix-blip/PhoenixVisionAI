(() => {
    "use strict";


    const $ = id =>
        document.getElementById(id);


    function escapeHtml(value) {

        return String(
            value ?? ""
        )
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }


    async function requestJson(
        url,
        options = {}
    ) {

        const response =
            await fetch(
                url,
                {
                    credentials:
                        "same-origin",

                    cache:
                        "no-store",

                    ...options,
                }
            );


        let data = {};

        try {

            data =
                await response.json();

        } catch (_) {

            data = {};
        }


        if (
            response.status === 401
        ) {

            window.location.replace(
                "/login"
            );

            throw new Error(
                "Session expirée."
            );
        }


        if (!response.ok) {

            throw new Error(
                data.message
                ||
                data.error
                ||
                `Erreur ${response.status}`
            );
        }


        return data;
    }


    function resultClass(
        result
    ) {

        if (result === "OK") {
            return "online";
        }

        if (
            result === "ATTENTION"
        ) {
            return "warning";
        }

        return "unavailable";
    }


    function formatDate(
        value
    ) {

        if (!value) {
            return "—";
        }


        const date =
            new Date(value);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return value;
        }


        return (
            new Intl.DateTimeFormat(
                "fr-FR",
                {
                    dateStyle:
                        "short",

                    timeStyle:
                        "medium",
                }
            )
            .format(date)
        );
    }


    function setBusy(
        busy
    ) {

        const diagnostic =
            $("system-run-diagnostic");

        const databases =
            $("system-check-databases");


        if (diagnostic) {
            diagnostic.disabled =
                busy;
        }

        if (databases) {
            databases.disabled =
                busy;
        }
    }


    function renderChecks(
        data
    ) {

        const result =
            $("system-diagnostic-result");

        result.textContent =
            data.result || "—";

        result.className =
            (
                "system-state "
                +
                resultClass(
                    data.result
                )
            );


        const container =
            $("system-diagnostic-checks");


        const checks =
            data.checks || [];


        if (!checks.length) {

            container.innerHTML = `
                <div class="system-loading-row">
                    Aucun contrôle retourné.
                </div>
            `;

            return;
        }


        container.innerHTML =
            checks.map(
                check => `
                    <div
                        class="system-diagnostic-check"
                    >

                        <div>

                            <strong>
                                ${escapeHtml(check.label)}
                            </strong>

                            <p>
                                ${escapeHtml(check.message)}
                            </p>

                        </div>

                        <span
                            class="system-state ${resultClass(check.result)}"
                        >
                            ${escapeHtml(check.result)}
                        </span>

                    </div>
                `
            )
            .join("");
    }


    function renderDatabaseCheck(
        data
    ) {

        const result =
            $("system-diagnostic-result");

        result.textContent =
            data.result || "—";

        result.className =
            (
                "system-state "
                +
                resultClass(
                    data.result
                )
            );


        const container =
            $("system-diagnostic-checks");


        container.innerHTML =
            (data.databases || [])
            .map(
                database => `
                    <div
                        class="system-diagnostic-check"
                    >

                        <div>

                            <strong>
                                ${escapeHtml(database.database)}
                            </strong>

                            <p>
                                Vérification rapide
                                d'intégrité SQLite.
                            </p>

                        </div>

                        <span
                            class="system-state ${resultClass(database.result)}"
                        >
                            ${escapeHtml(database.integrity)}
                        </span>

                    </div>
                `
            )
            .join("");
    }


    async function loadAudit() {

        const data =
            await requestJson(
                "/api/system/diagnostics/audit?limit=12"
            );


        const integrity =
            $("system-audit-integrity");


        integrity.textContent =
            data.integrity
                ? "AUDIT VALIDE"
                : "AUDIT INVALIDE";


        integrity.className =
            (
                "system-state "
                +
                (
                    data.integrity
                        ? "online"
                        : "unavailable"
                )
            );


        const body =
            $("system-diagnostic-audit-body");


        const events =
            data.events || [];


        if (!events.length) {

            body.innerHTML = `
                <tr>
                    <td
                        colspan="4"
                        class="system-empty"
                    >
                        Aucun diagnostic enregistré.
                    </td>
                </tr>
            `;

            return;
        }


        body.innerHTML =
            events.map(
                event => `
                    <tr>

                        <td>
                            ${escapeHtml(
                                formatDate(
                                    event.created_at
                                )
                            )}
                        </td>

                        <td>
                            ${escapeHtml(event.action)}
                        </td>

                        <td>
                            ${escapeHtml(event.actor)}
                        </td>

                        <td>
                            <span
                                class="system-state ${resultClass(event.result)}"
                            >
                                ${escapeHtml(event.result)}
                            </span>
                        </td>

                    </tr>
                `
            )
            .join("");
    }


    async function loadCapabilities() {

        const data =
            await requestJson(
                "/api/system/capabilities"
            );


        const actions =
            $("system-diagnostics-actions");

        const permission =
            $("system-diagnostics-permission");


        if (!data.diagnostics) {

            actions.classList.add(
                "hidden"
            );

            permission.classList.remove(
                "hidden"
            );

            return;
        }


        actions.classList.remove(
            "hidden"
        );

        permission.classList.add(
            "hidden"
        );


        $("system-run-diagnostic")
            .disabled = false;


        $("system-check-databases")
            .disabled =
                !data.database_check;


        await loadAudit();
    }


    async function runDiagnostic() {

        setBusy(
            true
        );


        try {

            const data =
                await requestJson(
                    "/api/system/diagnostics/run",
                    {
                        method:
                            "POST",
                    }
                );


            renderChecks(
                data
            );


            await loadAudit();


        } catch (error) {

            window.alert(
                error.message
            );


        } finally {

            setBusy(
                false
            );
        }
    }


    async function checkDatabases() {

        setBusy(
            true
        );


        try {

            const data =
                await requestJson(
                    "/api/system/diagnostics/database-check",
                    {
                        method:
                            "POST",

                        headers: {
                            "Content-Type":
                                "application/json",
                        },

                        body:
                            JSON.stringify(
                                {}
                            ),
                    }
                );


            renderDatabaseCheck(
                data
            );


            await loadAudit();


        } catch (error) {

            window.alert(
                error.message
            );


        } finally {

            setBusy(
                false
            );
        }
    }


    function bind() {

        const diagnostic =
            $("system-run-diagnostic");

        const databases =
            $("system-check-databases");


        if (diagnostic) {

            diagnostic.addEventListener(
                "click",
                runDiagnostic
            );
        }


        if (databases) {

            databases.addEventListener(
                "click",
                checkDatabases
            );
        }
    }


    async function boot() {

        bind();


        try {

            await loadCapabilities();

        } catch (error) {

            const permission =
                $("system-diagnostics-permission");

            if (permission) {

                permission.textContent =
                    error.message;

                permission.classList.remove(
                    "hidden"
                );
            }
        }
    }


    document.addEventListener(
        "DOMContentLoaded",
        boot
    );

})();
