(() => {

    "use strict";


    const byId = (id) =>
        document.getElementById(id);


    let currentReference = null;


    function value(
        item,
        fallback="—"
    ) {

        if (
            item === null
            ||
            item === undefined
            ||
            String(item).trim() === ""
        ) {

            return fallback;

        }

        return String(item);

    }


    function set(
        id,
        item,
        fallback="—"
    ) {

        const element = byId(
            id
        );

        if (!element) {

            return;

        }

        element.textContent =
            value(
                item,
                fallback
            );

    }


    function formatDateTime(
        input
    ) {

        if (!input) {

            return "—";

        }

        const date = new Date(
            input
        );

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return String(
                input
            );

        }

        return date.toLocaleString(
            "fr-FR"
        );

    }


    function formatConfidence(
        value
    ) {

        const number = Number(
            value
        );

        if (
            !Number.isFinite(
                number
            )
            ||
            number <= 0
        ) {

            return "—";

        }

        return `${number.toFixed(1)} %`;

    }


    function enabledSections(
        report
    ) {

        const sections = (
            Array.isArray(
                report.sections
            )
                ? report.sections
                : []
        );

        if (!sections.length) {

            return new Set([
                "summary",
                "vehicles",
                "events",
                "alerts",
                "anpr",
                "watchlist"
            ]);

        }

        return new Set(
            sections
        );

    }


    function applySections(
        report
    ) {

        const enabled = enabledSections(
            report
        );


        const mapping = {

            summary:
                "print-section-summary",

            vehicles:
                "print-section-vehicles",

            events:
                "print-section-events",

            alerts:
                "print-section-alerts",

            anpr:
                "print-section-anpr",

            watchlist:
                "print-section-watchlist"

        };


        for (
            const [
                name,
                id
            ]
            of Object.entries(
                mapping
            )
        ) {

            const section = byId(
                id
            );

            if (section) {

                section.hidden = (
                    !enabled.has(
                        name
                    )
                );

            }

        }

    }


    function fillTable(
        tbodyId,
        rows,
        columns
    ) {

        const tbody = byId(
            tbodyId
        );

        tbody.innerHTML = "";


        if (
            !Array.isArray(
                rows
            )
            ||
            rows.length === 0
        ) {

            const tr =
                document.createElement(
                    "tr"
                );

            const td =
                document.createElement(
                    "td"
                );

            td.colSpan =
                columns.length;

            td.className =
                "report-table-empty";

            td.textContent =
                "Aucune donnée enregistrée "
                +
                "pour cette section et cette période.";

            tr.appendChild(
                td
            );

            tbody.appendChild(
                tr
            );

            return;

        }


        for (
            const row
            of rows
        ) {

            const tr =
                document.createElement(
                    "tr"
                );


            for (
                const column
                of columns
            ) {

                const td =
                    document.createElement(
                        "td"
                    );

                let content = (
                    typeof column ===
                    "function"
                        ? column(
                            row
                        )
                        : row[
                            column
                        ]
                );

                td.textContent =
                    value(
                        content
                    );

                tr.appendChild(
                    td
                );

            }


            tbody.appendChild(
                tr
            );

        }

    }


    function renderCoverage(
        coverage
    ) {

        const container = byId(
            "data-coverage"
        );

        container.innerHTML = "";


        for (
            const [
                name,
                info
            ]
            of Object.entries(
                coverage
                ||
                {}
            )
        ) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "report-coverage-item";


            const strong =
                document.createElement(
                    "strong"
                );

            strong.textContent =
                value(
                    info.label,
                    name
                );


            const storage =
                document.createElement(
                    "span"
                );

            storage.textContent =
                "Stockage : "
                +
                value(
                    info.storage
                );


            const source =
                document.createElement(
                    "span"
                );

            source.textContent =
                "Source : "
                +
                value(
                    info.source
                );


            item.append(
                strong,
                storage,
                source
            );

            container.appendChild(
                item
            );

        }

    }


    function renderAudit(
        events
    ) {

        const container = byId(
            "audit-list"
        );

        container.innerHTML = "";


        if (
            !Array.isArray(
                events
            )
            ||
            events.length === 0
        ) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "report-print-audit-event";

            item.textContent =
                "Aucun événement d'audit.";

            container.appendChild(
                item
            );

            return;

        }


        for (
            const event
            of events
        ) {

            const item =
                document.createElement(
                    "div"
                );

            item.className =
                "report-print-audit-event";


            const action =
                document.createElement(
                    "strong"
                );

            action.textContent =
                value(
                    event.action
                );


            const actor =
                document.createElement(
                    "span"
                );

            actor.textContent =
                value(
                    event.actor
                )
                +
                " · "
                +
                value(
                    event.actor_role
                );


            const timestamp =
                document.createElement(
                    "span"
                );

            timestamp.textContent =
                formatDateTime(
                    event.timestamp
                );


            item.append(
                action,
                actor,
                timestamp
            );

            container.appendChild(
                item
            );

        }

    }


    function render(
        data
    ) {

        const report = (
            data.report
            ||
            {}
        );

        const snapshot = (
            report.snapshot
            ||
            {}
        );

        const summary = (
            snapshot.summary
            ||
            {}
        );

        const integrity = (
            data.integrity
            ||
            {}
        );


        currentReference =
            report.reference;


        document.title =
            value(
                report.reference,
                "Rapport Phoenix"
            )
            +
            " — Phoenix Vision AI";


        set(
            "p-reference",
            report.reference
        );

        set(
            "footer-reference",
            report.reference
        );

        set(
            "p-status",
            report.status
        );

        set(
            "p-version",
            report.version
        );

        set(
            "p-period-start",
            formatDateTime(
                report.period_start
            )
        );

        set(
            "p-period-end",
            formatDateTime(
                report.period_end
            )
        );

        set(
            "p-scope",
            report.scope
        );

        set(
            "p-generated-by",
            report.generated_by
        );

        set(
            "p-generated-role",
            report.generated_role
        );

        set(
            "p-generated-at",
            formatDateTime(
                report.generated_at
            )
        );

        set(
            "p-prepared-by",
            data.prepared_by
        );

        set(
            "p-prepared-role",
            data.prepared_role
        );

        set(
            "p-prepared-at",
            formatDateTime(
                data.prepared_at
            )
        );


        set(
            "kpi-vehicles",
            summary.vehicles
            ??
            0
        );

        set(
            "kpi-events",
            summary.events
            ??
            0
        );

        set(
            "kpi-alerts",
            summary.alerts
            ??
            0
        );

        set(
            "kpi-plates",
            summary.plates_detected
            ??
            0
        );

        set(
            "kpi-watchlist",
            summary.watchlist_active_in_period
            ??
            0
        );

        set(
            "kpi-matches",
            summary.watchlist_matches
            ??
            0
        );


        set(
            "sum-threats",
            summary.threat_vehicles
            ??
            0
        );

        set(
            "sum-critical-alerts",
            summary.alerts_critical
            ??
            0
        );

        set(
            "sum-ack-alerts",
            summary.alerts_acknowledged
            ??
            0
        );

        set(
            "sum-validated-plates",
            summary.plates_validated
            ??
            0
        );

        set(
            "sum-review-plates",
            summary.plates_to_review
            ??
            0
        );

        set(
            "sum-approved-watchlist",
            summary.watchlist_approved
            ??
            0
        );


        const snapshotValid =
            Boolean(
                integrity.snapshot_valid
            );

        const auditValid =
            Boolean(
                integrity.audit_valid
            );


        set(
            "integrity-snapshot",
            snapshotValid
                ? "VALIDÉ"
                : "ÉCHEC"
        );

        set(
            "integrity-audit",
            auditValid
                ? "VALIDÉ"
                : "ÉCHEC"
        );

        set(
            "integrity-hash",
            report.snapshot_hash
        );


        byId(
            "integrity-snapshot"
        ).className =
            snapshotValid
                ? "integrity-ok"
                : "integrity-error";


        byId(
            "integrity-audit"
        ).className =
            auditValid
                ? "integrity-ok"
                : "integrity-error";


        applySections(
            report
        );


        fillTable(

            "table-vehicles",

            snapshot.history
            ?.recent
            ||
            [],

            [
                row =>
                    String(
                        row.uuid
                        ||
                        "—"
                    ).slice(
                        0,
                        12
                    ),

                row =>
                    row.label,

                row =>
                    row.plate
                    ||
                    "NON LUE",

                row =>
                    formatDateTime(
                        row.last_seen
                        ||
                        row.created_at
                    ),

                row =>
                    row.last_camera,

                row =>
                    row.threat_level
            ]

        );


        fillTable(

            "table-events",

            snapshot.events
            ?.recent
            ||
            [],

            [
                row =>
                    row.type,

                row =>
                    row.level,

                row =>
                    row.description,

                row =>
                    row.vehicle_uuid,

                row =>
                    formatDateTime(
                        row.timestamp
                    )
            ]

        );


        fillTable(

            "table-alerts",

            snapshot.alerts
            ?.recent
            ||
            [],

            [
                row =>
                    row.type,

                row =>
                    row.level,

                row =>
                    row.status,

                row =>
                    row.message,

                row =>
                    formatDateTime(
                        row.timestamp
                    )
            ]

        );


        fillTable(

            "table-anpr",

            snapshot.anpr
            ?.recent
            ||
            [],

            [
                row =>
                    row.plate,

                row =>
                    formatConfidence(
                        row.plate_confidence
                    ),

                row =>
                    row.plate_status,

                row =>
                    formatDateTime(
                        row.plate_last_seen
                        ||
                        row.last_seen
                    ),

                row =>
                    row.last_camera
            ]

        );


        fillTable(

            "table-watchlist",

            snapshot.watchlist
            ?.recent
            ||
            [],

            [
                row =>
                    row.plate,

                row =>
                    row.category,

                row =>
                    row.priority,

                row =>
                    row.status,

                row =>
                    formatDateTime(
                        row.created_at
                    ),

                row =>
                    row.approved_by
            ]

        );


        renderCoverage(
            snapshot.data_coverage
        );


        renderAudit(
            data.audit
        );

    }


    async function loadReport() {

        const parts =
            window.location.pathname
            .split("/")
            .filter(Boolean);


        if (
            parts.length < 3
            ||
            parts[
                parts.length - 1
            ] !== "print"
        ) {

            document.body.textContent =
                "Référence de rapport invalide.";

            return;

        }


        const reference =
            parts[
                parts.length - 2
            ];


        const response =
            await fetch(

                "/api/reports/"
                +
                encodeURIComponent(
                    reference
                )
                +
                "/printable",

                {
                    credentials:
                        "same-origin",

                    cache:
                        "no-store"
                }

            );


        if (response.status === 403) {

            document.body.textContent =
                "Accès refusé : "
                +
                "permission d'impression requise.";

            return;

        }


        if (!response.ok) {

            document.body.textContent =
                "Impossible de charger le rapport.";

            return;

        }


        const data =
            await response.json();


        render(
            data
        );

    }


    async function requestPrint() {

        if (!currentReference) {

            return;

        }


        const button = byId(
            "print-button"
        );

        const message = byId(
            "print-message"
        );


        button.disabled = true;

        message.hidden = false;

        message.textContent =
            "Préparation et traçabilité "
            +
            "de la demande d'impression...";


        try {

            const response =
                await fetch(

                    "/api/reports/"
                    +
                    encodeURIComponent(
                        currentReference
                    )
                    +
                    "/print-requested",

                    {
                        method:
                            "POST",

                        credentials:
                            "same-origin",

                        cache:
                            "no-store"
                    }

                );


            if (!response.ok) {

                throw new Error(
                    "La demande d'impression "
                    +
                    "n'a pas pu être enregistrée."
                );

            }


            const data =
                await response.json();


            set(
                "p-print-requested",
                formatDateTime(
                    data.requested_at
                )
            );


            renderAudit(
                data.audit
            );


            message.textContent =
                "Demande tracée. "
                +
                "Ouverture de la fenêtre d'impression.";


            setTimeout(
                () => {

                    window.print();

                },
                120
            );


        }

        catch (error) {

            message.textContent =
                error.message;

        }

        finally {

            setTimeout(
                () => {

                    button.disabled = false;

                },
                500
            );

        }

    }


    document.addEventListener(
        "DOMContentLoaded",
        async () => {

            await loadReport();


            const button = byId(
                "print-button"
            );


            if (button) {

                button.addEventListener(
                    "click",
                    requestPrint
                );

            }

        }
    );

})();
