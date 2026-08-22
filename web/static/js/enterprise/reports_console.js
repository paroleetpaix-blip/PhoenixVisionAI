(() => {

    "use strict";


    const byId = (id) =>
        document.getElementById(id);


    const state = {

        capabilities: {
            view: false,
            generate: false,
            print: false,
            export_pdf: false
        },

        reports: []

    };


    function escapeHtml(value) {

        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");

    }


    function dateInputValue(date) {

        const year = date.getFullYear();

        const month = String(
            date.getMonth() + 1
        ).padStart(
            2,
            "0"
        );

        const day = String(
            date.getDate()
        ).padStart(
            2,
            "0"
        );

        return `${year}-${month}-${day}`;

    }


    function startOfWeek(date) {

        const result = new Date(date);

        const day = result.getDay();

        const offset = (
            day === 0
                ? -6
                : 1 - day
        );

        result.setDate(
            result.getDate() + offset
        );

        return result;

    }


    function endOfWeek(date) {

        const result = startOfWeek(
            date
        );

        result.setDate(
            result.getDate() + 6
        );

        return result;

    }


    function setPeriodPreset() {

        const preset = byId(
            "report-period-preset"
        ).value;

        const today = new Date();

        let start = new Date(today);

        let end = new Date(today);


        if (preset === "yesterday") {

            start.setDate(
                start.getDate() - 1
            );

            end = new Date(start);

        }


        else if (preset === "week") {

            start = startOfWeek(
                today
            );

            end = new Date(today);

        }


        else if (
            preset ===
            "previous_week"
        ) {

            const currentStart = (
                startOfWeek(
                    today
                )
            );

            start = new Date(
                currentStart
            );

            start.setDate(
                start.getDate() - 7
            );

            end = endOfWeek(
                start
            );

        }


        else if (preset === "month") {

            start = new Date(
                today.getFullYear(),
                today.getMonth(),
                1
            );

            end = new Date(today);

        }


        else if (
            preset ===
            "previous_month"
        ) {

            start = new Date(
                today.getFullYear(),
                today.getMonth() - 1,
                1
            );

            end = new Date(
                today.getFullYear(),
                today.getMonth(),
                0
            );

        }


        else if (preset === "quarter") {

            const quarterStart = (
                Math.floor(
                    today.getMonth() / 3
                ) * 3
            );

            start = new Date(
                today.getFullYear(),
                quarterStart,
                1
            );

            end = new Date(today);

        }


        else if (preset === "semester") {

            const semesterStart = (
                today.getMonth() < 6
                    ? 0
                    : 6
            );

            start = new Date(
                today.getFullYear(),
                semesterStart,
                1
            );

            end = new Date(today);

        }


        else if (preset === "year") {

            start = new Date(
                today.getFullYear(),
                0,
                1
            );

            end = new Date(today);

        }


        else if (preset === "custom") {

            return;

        }


        byId(
            "report-period-start"
        ).value = dateInputValue(
            start
        );

        byId(
            "report-period-end"
        ).value = dateInputValue(
            end
        );

    }


    function formatDateTime(value) {

        if (!value) {

            return "—";

        }

        const date = new Date(
            value
        );

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return value;

        }

        return date.toLocaleString(
            "fr-FR"
        );

    }


    function formatDate(value) {

        if (!value) {

            return "—";

        }

        const date = new Date(
            value
        );

        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return value;

        }

        return date.toLocaleDateString(
            "fr-FR"
        );

    }


    function setMessage(
        message,
        kind=""
    ) {

        const element = byId(
            "reports-message"
        );

        if (!message) {

            element.hidden = true;

            element.textContent = "";

            element.className =
                "reports-message";

            return;

        }

        element.hidden = false;

        element.className =
            `reports-message ${kind}`;

        element.textContent =
            message;

    }


    async function fetchJson(
        url,
        options={}
    ) {

        const response = await fetch(
            url,
            options
        );

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.message
                ||
                data.error
                ||
                "Erreur Phoenix"
            );

        }

        return data;

    }


    function currentPeriod() {

        return {

            start:
                byId(
                    "report-period-start"
                ).value,

            end:
                byId(
                    "report-period-end"
                ).value

        };

    }


    async function loadCapabilities() {

        const data = await fetchJson(
            "/api/reports/capabilities"
        );

        state.capabilities = (
            data.capabilities
            ||
            state.capabilities
        );

        const generateButton = byId(
            "report-generate-button"
        );

        generateButton.hidden = (
            !state.capabilities.generate
        );

    }


    function renderPreview(
        snapshot
    ) {

        const summary = (
            snapshot.summary
            ||
            {}
        );

        byId(
            "report-kpi-vehicles"
        ).textContent = (
            summary.vehicles
            ??
            0
        );

        byId(
            "report-kpi-events"
        ).textContent = (
            summary.events
            ??
            0
        );

        byId(
            "report-kpi-alerts"
        ).textContent = (
            summary.alerts
            ??
            0
        );

        byId(
            "report-kpi-plates"
        ).textContent = (
            summary.plates_detected
            ??
            0
        );

        byId(
            "report-kpi-watchlist"
        ).textContent = (
            summary.watchlist_active_in_period
            ??
            0
        );

        byId(
            "report-kpi-matches"
        ).textContent = (
            summary.watchlist_matches
            ??
            0
        );

    }


    async function refreshPreview() {

        const period = currentPeriod();

        if (
            !period.start
            ||
            !period.end
        ) {

            return;

        }

        try {

            const params = new URLSearchParams({
                period_start:
                    period.start,

                period_end:
                    period.end
            });

            const data = await fetchJson(
                "/api/reports/preview?"
                +
                params.toString()
            );

            renderPreview(
                data.snapshot
            );

        }

        catch (error) {

            setMessage(
                error.message,
                "error"
            );

        }

    }


    function selectedSections() {

        return Array.from(
            document.querySelectorAll(
                ".report-section-options "
                +
                'input[type="checkbox"]:checked'
            )
        ).map(
            (element) =>
                element.value
        );

    }


    async function generateReport() {

        const period = currentPeriod();

        if (
            !period.start
            ||
            !period.end
        ) {

            setMessage(
                "Sélectionne une période complète.",
                "error"
            );

            return;

        }

        const button = byId(
            "report-generate-button"
        );

        button.disabled = true;

        setMessage(
            "Génération du rapport en cours..."
        );

        try {

            const data = await fetchJson(
                "/api/reports/generate",
                {
                    method:
                        "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({

                            period_start:
                                period.start,

                            period_end:
                                period.end,

                            scope:
                                byId(
                                    "report-scope"
                                ).value,

                            filters:
                                {},

                            sections:
                                selectedSections()

                        })
                }
            );

            const reference = (
                data.report.reference
            );

            setMessage(
                "Rapport généré : "
                +
                reference,
                "success"
            );

            await loadReports();

            await openReport(
                reference
            );

        }

        catch (error) {

            setMessage(
                error.message,
                "error"
            );

        }

        finally {

            button.disabled = false;

        }

    }


    function renderReports(
        reports
    ) {

        const tbody = byId(
            "reports-table-body"
        );

        const empty = byId(
            "reports-empty"
        );

        const count = byId(
            "reports-count"
        );

        state.reports = Array.isArray(
            reports
        )
            ? reports
            : [];

        if (state.reports.length === 0) {

            count.textContent =
                "0 rapport";

        }

        else if (state.reports.length === 1) {

            count.textContent =
                "1 rapport trouvé";

        }

        else {

            count.textContent =
                `${state.reports.length} rapports trouvés`;

        }

        tbody.innerHTML = "";

        empty.hidden = (
            state.reports.length > 0
        );

        for (
            const report
            of state.reports
        ) {

            const row = document.createElement(
                "tr"
            );

            row.innerHTML = `
                <td>
                    ${escapeHtml(report.reference)}
                </td>

                <td>
                    ${escapeHtml(
                        report.report_type
                        ||
                        "—"
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        formatDate(
                            report.period_start
                        )
                    )}
                    →
                    ${escapeHtml(
                        formatDate(
                            report.period_end
                        )
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        report.generated_by
                        ||
                        "—"
                    )}
                </td>

                <td>
                    <span class="report-status">
                        ${escapeHtml(
                            report.status
                            ||
                            "—"
                        )}
                    </span>
                </td>

                <td>
                    <div class="report-row-actions">

                        <button
                            class="report-mini-button"
                            data-action="view"
                            data-reference="${escapeHtml(report.reference)}"
                        >
                            CONSULTER
                        </button>

                        <button
                            class="report-mini-button"
                            data-action="audit"
                            data-reference="${escapeHtml(report.reference)}"
                        >
                            JOURNAL
                        </button>

                        <button
                            class="report-mini-button"
                            data-action="print"
                            data-reference="${escapeHtml(report.reference)}"
                            ${
                                state.capabilities.print
                                    ? ""
                                    : "disabled"
                            }
                        >
                            IMPRIMER
                        </button>

                        <button
                            class="report-mini-button"
                            data-action="pdf"
                            data-reference="${escapeHtml(report.reference)}"
                            ${
                                state.capabilities.export_pdf
                                    ? ""
                                    : "disabled"
                            }
                        >
                            PDF
                        </button>

                    </div>
                </td>
            `;

            tbody.appendChild(
                row
            );

        }

    }


    async function loadReports() {

        try {

            const data = await fetchJson(
                "/api/reports?limit=100"
            );

            renderReports(
                data.reports
            );

        }

        catch (error) {

            setMessage(
                error.message,
                "error"
            );

        }

    }


    async function searchReports() {

        const params = new URLSearchParams();

        const reference = byId(
            "report-search-reference"
        ).value.trim();

        const author = byId(
            "report-search-author"
        ).value.trim();

        const status = byId(
            "report-search-status"
        ).value;

        const start = byId(
            "report-search-start"
        ).value;

        const end = byId(
            "report-search-end"
        ).value;


        if (reference) {

            params.set(
                "reference",
                reference
            );

        }


        if (author) {

            params.set(
                "generated_by",
                author
            );

        }


        if (status) {

            params.set(
                "status",
                status
            );

        }


        if (start) {

            params.set(
                "period_start",
                start
                +
                "T00:00:00"
            );

        }


        if (end) {

            params.set(
                "period_end",
                end
                +
                "T23:59:59.999999"
            );

        }


        try {

            const data = await fetchJson(
                "/api/reports/search?"
                +
                params.toString()
            );

            renderReports(
                data.reports
            );

        }

        catch (error) {

            setMessage(
                error.message,
                "error"
            );

        }

    }


    function resetSearch() {

        byId(
            "report-search-reference"
        ).value = "";

        byId(
            "report-search-author"
        ).value = "";

        byId(
            "report-search-status"
        ).value = "";

        byId(
            "report-search-start"
        ).value = "";

        byId(
            "report-search-end"
        ).value = "";

        loadReports();

    }


    function renderReportDetail(
        report,
        integrity
    ) {

        const content = byId(
            "report-detail-content"
        );

        const snapshotValid = (
            integrity
            &&
            integrity.snapshot_valid
        );

        const auditValid = (
            integrity
            &&
            integrity.audit_valid
        );

        content.innerHTML = `

            <div class="report-detail-reference">
                ${escapeHtml(report.reference)}
            </div>

            <div class="report-detail-subtitle">
                ${escapeHtml(
                    report.title
                    ||
                    "Rapport Phoenix"
                )}
            </div>


            <div class="report-detail-grid">

                <div class="report-detail-card">
                    <span>STATUT</span>
                    <strong>
                        ${escapeHtml(report.status)}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>TYPE</span>
                    <strong>
                        ${escapeHtml(report.report_type)}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>DÉBUT</span>
                    <strong>
                        ${escapeHtml(
                            formatDateTime(
                                report.period_start
                            )
                        )}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>FIN</span>
                    <strong>
                        ${escapeHtml(
                            formatDateTime(
                                report.period_end
                            )
                        )}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>GÉNÉRÉ PAR</span>
                    <strong>
                        ${escapeHtml(report.generated_by)}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>RÔLE</span>
                    <strong>
                        ${escapeHtml(report.generated_role)}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>GÉNÉRÉ LE</span>
                    <strong>
                        ${escapeHtml(
                            formatDateTime(
                                report.generated_at
                            )
                        )}
                    </strong>
                </div>

                <div class="report-detail-card">
                    <span>PÉRIMÈTRE</span>
                    <strong>
                        ${escapeHtml(
                            report.scope
                            ||
                            "—"
                        )}
                    </strong>
                </div>

            </div>


            <div class="report-integrity-box">

                <strong>
                    ${
                        snapshotValid
                            &&
                        auditValid
                            ? "INTÉGRITÉ VALIDÉE"
                            : "VÉRIFICATION REQUISE"
                    }
                </strong>

                <code>
                    SHA-256 :
                    ${escapeHtml(
                        report.snapshot_hash
                        ||
                        "—"
                    )}
                </code>

            </div>


            <div class="report-detail-actions">

                <button
                    id="report-load-audit"
                    class="phx-button"
                    type="button"
                >
                    JOURNAL D'AUDIT
                </button>

                <button
                    id="report-print-button"
                    class="phx-button"
                    type="button"
                    ${
                        state.capabilities.print
                            ? ""
                            : "disabled"
                    }
                >
                    IMPRIMER
                </button>

                <button
                    id="report-pdf-button"
                    class="phx-button"
                    type="button"
                    ${
                        state.capabilities.export_pdf
                            ? ""
                            : "disabled"
                    }
                >
                    EXPORTER PDF
                </button>

            </div>


            <div
                id="report-audit-container"
                class="report-audit-list"
                hidden
            ></div>
        `;

        byId(
            "report-load-audit"
        ).addEventListener(
            "click",
            () =>
                loadAudit(
                    report.reference
                )
        );


        const printButton = byId(
            "report-print-button"
        );


        if (printButton) {

            printButton.addEventListener(
                "click",
                () =>
                    openPrint(
                        report.reference
                    )
            );

        }


        const pdfButton = byId(
            "report-pdf-button"
        );


        if (pdfButton) {

            pdfButton.addEventListener(
                "click",
                () =>
                    exportPdf(
                        report.reference
                    )
            );

        }

    }


    function exportPdf(
        reference
    ) {

        if (
            !reference
            ||
            !state.capabilities.export_pdf
        ) {

            return;

        }


        const link =
            document.createElement(
                "a"
            );


        link.href =
            "/api/reports/"
            +
            encodeURIComponent(
                reference
            )
            +
            "/pdf";


        link.style.display =
            "none";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        setMessage(
            "Export PDF demandé pour "
            +
            reference
            +
            "."
        );

    }


    function openPrint(
        reference
    ) {

        if (
            !reference
            ||
            !state.capabilities.print
        ) {

            return;

        }


        const url =
            "/reports/"
            +
            encodeURIComponent(
                reference
            )
            +
            "/print";


        window.open(
            url,
            "_blank"
        );

    }


    async function openReport(
        reference,
        showAudit=false
    ) {

        try {

            const data = await fetchJson(
                "/api/reports/"
                +
                encodeURIComponent(
                    reference
                )
            );

            renderReportDetail(
                data.report,
                data.integrity
            );

            byId(
                "report-detail-panel"
            ).hidden = false;

            if (showAudit) {

                await loadAudit(
                    reference
                );

            }

        }

        catch (error) {

            setMessage(
                error.message,
                "error"
            );

        }

    }


    async function loadAudit(
        reference
    ) {

        try {

            const data = await fetchJson(
                "/api/reports/"
                +
                encodeURIComponent(
                    reference
                )
                +
                "/audit"
            );

            const container = byId(
                "report-audit-container"
            );

            container.hidden = false;

            const events = (
                Array.isArray(
                    data.audit
                )
                    ? data.audit
                    : []
            );

            container.innerHTML = `
                <h3>JOURNAL D'AUDIT</h3>

                ${
                    events.length
                        ? events.map(
                            (event) => `
                                <div class="report-audit-event">

                                    <strong>
                                        ${escapeHtml(event.action)}
                                    </strong>

                                    <span>
                                        ${escapeHtml(event.actor)}
                                        ·
                                        ${escapeHtml(event.actor_role || "—")}
                                        ·
                                        ${escapeHtml(
                                            formatDateTime(
                                                event.timestamp
                                            )
                                        )}
                                    </span>

                                </div>
                            `
                        ).join("")
                        : `
                            <div class="report-audit-event">
                                <span>
                                    Aucun événement d'audit.
                                </span>
                            </div>
                        `
                }
            `;

        }

        catch (error) {

            setMessage(
                error.message,
                "error"
            );

        }

    }


    function closeDetail() {

        byId(
            "report-detail-panel"
        ).hidden = true;

    }


    document.addEventListener(
        "DOMContentLoaded",
        async () => {

            setPeriodPreset();


            byId(
                "report-period-preset"
            ).addEventListener(
                "change",
                async () => {

                    setPeriodPreset();

                    await refreshPreview();

                }
            );


            byId(
                "report-period-start"
            ).addEventListener(
                "change",
                () => {

                    byId(
                        "report-period-preset"
                    ).value =
                        "custom";

                }
            );


            byId(
                "report-period-end"
            ).addEventListener(
                "change",
                () => {

                    byId(
                        "report-period-preset"
                    ).value =
                        "custom";

                }
            );


            byId(
                "report-preview-button"
            ).addEventListener(
                "click",
                refreshPreview
            );


            byId(
                "report-generate-button"
            ).addEventListener(
                "click",
                generateReport
            );


            byId(
                "report-search-button"
            ).addEventListener(
                "click",
                searchReports
            );


            byId(
                "report-search-reset"
            ).addEventListener(
                "click",
                resetSearch
            );


            byId(
                "report-detail-close"
            ).addEventListener(
                "click",
                closeDetail
            );


            byId(
                "reports-table-body"
            ).addEventListener(
                "click",
                async (event) => {

                    const button = (
                        event.target.closest(
                            "[data-reference]"
                        )
                    );

                    if (!button) {

                        return;

                    }

                    const reference = (
                        button.dataset.reference
                    );

                    const action = (
                        button.dataset.action
                    );


                    if (action === "print") {

                        openPrint(
                            reference
                        );

                        return;

                    }


                    if (action === "pdf") {

                        exportPdf(
                            reference
                        );

                        return;

                    }


                    await openReport(
                        reference,
                        action === "audit"
                    );

                }
            );


            try {

                await loadCapabilities();

                await refreshPreview();

                await loadReports();

            }

            catch (error) {

                setMessage(
                    error.message,
                    "error"
                );

            }

        }
    );

})();
