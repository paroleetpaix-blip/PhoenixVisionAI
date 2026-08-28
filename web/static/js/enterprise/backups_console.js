(() => {
    "use strict";

    const state = {
        capabilities: null,
        restore: null,
        backups: [],
        selectedRestoreId: null,
    };


    const byId = (id) => document.getElementById(id);


    const escapeHtml = (value) => String(
        value ?? ""
    )
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");


    const pick = (object, keys, fallback = null) => {
        if (!object || typeof object !== "object") {
            return fallback;
        }

        for (const key of keys) {
            if (
                Object.prototype.hasOwnProperty.call(
                    object,
                    key
                )
                &&
                object[key] !== null
                &&
                object[key] !== undefined
            ) {
                return object[key];
            }
        }

        return fallback;
    };


    const showToast = (message, error = false) => {
        const toast = byId("backup-toast");

        if (!toast) {
            return;
        }

        toast.textContent = String(message);

        toast.classList.toggle(
            "is-error",
            Boolean(error)
        );

        toast.classList.add(
            "is-visible"
        );

        window.clearTimeout(
            showToast.timer
        );

        showToast.timer = window.setTimeout(
            () => {
                toast.classList.remove(
                    "is-visible"
                );
            },
            3200
        );
    };


    const fetchJson = async (url, options = {}) => {
        const response = await fetch(
            url,
            {
                credentials: "same-origin",
                ...options,
            }
        );


        if (response.status === 401) {
            window.location.href = "/login";
            throw new Error(
                "Session Phoenix expirée."
            );
        }


        let payload = null;

        try {
            payload = await response.json();
        }
        catch {
            payload = {
                success: false,
                message: "Réponse serveur invalide.",
            };
        }


        if (!response.ok) {
            throw new Error(
                payload.message
                ||
                payload.status
                ||
                `Erreur HTTP ${response.status}`
            );
        }


        return payload;
    };


    const formatDate = (value) => {
        if (!value) {
            return "—";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return String(value);
        }

        return new Intl.DateTimeFormat(
            "fr-FR",
            {
                dateStyle: "medium",
                timeStyle: "short",
            }
        ).format(date);
    };


    const formatBytes = (value) => {
        const bytes = Number(value);

        if (!Number.isFinite(bytes) || bytes < 0) {
            return "—";
        }

        if (bytes < 1024) {
            return `${bytes} o`;
        }

        const units = [
            "Ko",
            "Mo",
            "Go",
            "To",
        ];

        let size = bytes / 1024;
        let index = 0;

        while (
            size >= 1024
            &&
            index < units.length - 1
        ) {
            size /= 1024;
            index += 1;
        }

        return `${size.toFixed(
            size >= 10 ? 1 : 2
        )} ${units[index]}`;
    };


    const translateType = (value) => {
        const map = {
            MANUAL: "Manuelle",
            PRE_RESTORE: "Pré-restauration",
            MIGRATED: "Migrée",
            AUTOMATIC: "Automatique",
            DAILY: "Quotidienne",
            WEEKLY: "Hebdomadaire",
            MONTHLY: "Mensuelle",
        };

        return map[String(value || "").toUpperCase()]
            ||
            String(value || "—");
    };


    const translateStatus = (value) => {
        const status = String(
            value || ""
        ).toUpperCase();

        const map = {
            AVAILABLE: "Disponible",
            VALID: "Valide",
            INVALID: "Invalide",
            COMPLETE: "Complète",
            RESTORE_PENDING: "En attente",
            RESTORE_IN_PROGRESS: "En cours",
            IDLE: "Aucune en attente",
        };

        return map[status]
            ||
            String(value || "—");
    };


    const statusClass = (value) => {
        const status = String(
            value || ""
        ).toUpperCase();

        if (
            status === "AVAILABLE"
            ||
            status === "VALID"
            ||
            status === "COMPLETE"
        ) {
            return "is-valid";
        }

        if (status === "INVALID") {
            return "is-invalid";
        }

        return "";
    };


    const backupId = (backup) => pick(
        backup,
        [
            "backup_id",
            "id",
        ],
        ""
    );


    const backupVersion = (backup) => pick(
        backup,
        [
            "application_version",
            "version",
        ],
        "—"
    );


    const backupDate = (backup) => pick(
        backup,
        [
            "created_at",
            "created",
            "timestamp",
        ]
    );


    const renderCapabilities = () => {
        const capabilities = state.capabilities || {};

        const create = byId(
            "backup-create"
        );

        if (create) {
            create.hidden = !capabilities.create;
        }


        byId(
            "backup-stat-version"
        ).textContent = (
            capabilities.application_version
            ||
            "—"
        );


        const banner = byId(
            "backup-live-banner"
        );

        const title = byId(
            "backup-live-title"
        );

        const text = byId(
            "backup-live-text"
        );


        if (capabilities.live_restore_enabled) {
            banner.classList.remove(
                "is-locked"
            );

            banner.classList.add(
                "is-ready"
            );

            title.textContent =
                "Restauration LIVE autorisée";

            text.textContent =
                "Le moteur de restauration est disponible sous contrôle des autorisations Phoenix.";
        }
        else {
            banner.classList.remove(
                "is-ready"
            );

            banner.classList.add(
                "is-locked"
            );

            title.textContent =
                "Restauration LIVE verrouillée";

            text.textContent =
                "Aucune écriture de restauration ne peut être déclenchée depuis cette console.";
        }
    };


    const renderAutomation = () => {
        const automation = (
            state.capabilities?.automation
            ||
            {}
        );


        const status = byId(
            "backup-auto-status"
        );

        const interval = byId(
            "backup-auto-interval"
        );

        const next = byId(
            "backup-auto-next"
        );

        const retention = byId(
            "backup-auto-retention"
        );


        if (status) {
            if (
                automation.enabled
                &&
                automation.running
            ) {
                status.textContent =
                    "Actives";

                status.classList.add(
                    "is-active"
                );
            }
            else if (automation.enabled) {
                status.textContent =
                    "Activées — service arrêté";

                status.classList.remove(
                    "is-active"
                );
            }
            else {
                status.textContent =
                    "Désactivées";

                status.classList.remove(
                    "is-active"
                );
            }
        }


        if (interval) {
            const seconds = Number(
                automation.interval_seconds
            );


            if (
                Number.isFinite(seconds)
                &&
                seconds > 0
            ) {
                const hours = (
                    seconds
                    /
                    3600
                );

                interval.textContent = (
                    hours === 1
                    ?
                    "Toutes les heures"
                    :
                    `Toutes les ${hours} h`
                );
            }
            else {
                interval.textContent = "—";
            }
        }


        if (next) {
            next.textContent = (
                automation.next_due_at
                ?
                formatDate(
                    automation.next_due_at
                )
                :
                "À déterminer"
            );
        }


        if (retention) {
            const policy = (
                automation.retention
                ||
                {}
            );


            retention.textContent = (
                `${policy.hourly_hours ?? "—"} h`
                +
                " / "
                +
                `${policy.daily_days ?? "—"} j`
                +
                " / "
                +
                `${policy.weekly_weeks ?? "—"} sem.`
                +
                " / "
                +
                `${policy.monthly_months ?? "—"} mois`
            );
        }
    };


    const renderRestoreState = () => {
        const restore = state.restore || {};

        const status = (
            restore.status
            ||
            "IDLE"
        );

        byId(
            "backup-stat-restore"
        ).textContent = translateStatus(
            status
        );
    };


    const renderStats = () => {
        byId(
            "backup-stat-count"
        ).textContent = String(
            state.backups.length
        );


        const latest = state.backups[0];

        byId(
            "backup-stat-latest"
        ).textContent = latest
            ?
            formatDate(
                backupDate(latest)
            )
            :
            "Aucune";
    };


    const actionButton = (
        action,
        id,
        label,
        extraClass = "",
        disabled = false,
        title = ""
    ) => {
        return `
            <button
                type="button"
                class="backup-table-button ${escapeHtml(extraClass)}"
                data-action="${escapeHtml(action)}"
                data-backup-id="${escapeHtml(id)}"
                ${disabled ? "disabled" : ""}
                ${title ? `title="${escapeHtml(title)}"` : ""}
            >
                ${escapeHtml(label)}
            </button>
        `;
    };


    const renderTable = () => {
        const body = byId(
            "backup-table-body"
        );

        const catalogState = byId(
            "backup-catalog-state"
        );


        catalogState.textContent =
            `${state.backups.length} sauvegarde${state.backups.length > 1 ? "s" : ""}`;


        if (!state.backups.length) {
            body.innerHTML = `
                <tr>
                    <td
                        colspan="7"
                        class="backup-empty-cell"
                    >
                        Aucune sauvegarde Phoenix disponible.
                    </td>
                </tr>
            `;

            return;
        }


        const capabilities = (
            state.capabilities
            ||
            {}
        );


        body.innerHTML = state.backups.map(
            (backup) => {
                const id = backupId(
                    backup
                );

                const type = pick(
                    backup,
                    [
                        "backup_type",
                        "type",
                    ],
                    "—"
                );

                const status = pick(
                    backup,
                    [
                        "status",
                    ],
                    "—"
                );

                const fileCount = pick(
                    backup,
                    [
                        "file_count",
                    ],
                    "—"
                );

                const version = backupVersion(
                    backup
                );

                const migrateRequired = (
                    capabilities.application_version
                    &&
                    version
                    &&
                    version !== "—"
                    &&
                    version !== capabilities.application_version
                );

                const restoreDisabled = (
                    !capabilities.restore
                    ||
                    !capabilities.live_restore_enabled
                );

                const restoreTitle = (
                    !capabilities.live_restore_enabled
                    ?
                    "Restauration LIVE verrouillée"
                    :
                    ""
                );


                let actions = "";

                actions += actionButton(
                    "details",
                    id,
                    "Détails"
                );


                if (capabilities.verify) {
                    actions += actionButton(
                        "verify",
                        id,
                        "Vérifier"
                    );
                }


                if (
                    capabilities.migrate
                    &&
                    migrateRequired
                ) {
                    actions += actionButton(
                        "migrate",
                        id,
                        "Migrer"
                    );
                }


                if (capabilities.restore) {
                    actions += actionButton(
                        "restore",
                        id,
                        "Restaurer",
                        "is-danger",
                        restoreDisabled,
                        restoreTitle
                    );
                }


                return `
                    <tr data-row-backup-id="${escapeHtml(id)}">

                        <td>
                            <span class="backup-id">
                                ${escapeHtml(id)}
                            </span>
                        </td>

                        <td>
                            ${escapeHtml(
                                translateType(type)
                            )}
                        </td>

                        <td class="backup-subtle">
                            ${escapeHtml(
                                formatDate(
                                    backupDate(backup)
                                )
                            )}
                        </td>

                        <td>
                            ${escapeHtml(version)}
                        </td>

                        <td>
                            ${escapeHtml(fileCount)}
                        </td>

                        <td>
                            <span
                                class="backup-status ${statusClass(status)}"
                                data-status-for="${escapeHtml(id)}"
                            >
                                ${escapeHtml(
                                    translateStatus(status)
                                )}
                            </span>
                        </td>

                        <td>
                            <div class="backup-row-actions">
                                ${actions}
                            </div>
                        </td>

                    </tr>
                `;
            }
        ).join("");
    };


    const loadData = async () => {
        const [
            capabilities,
            catalog,
            restore,
        ] = await Promise.all([
            fetchJson(
                "/api/backups/capabilities"
            ),
            fetchJson(
                "/api/backups"
            ),
            fetchJson(
                "/api/backups/restore/status"
            ),
        ]);


        state.capabilities = capabilities;

        state.restore = restore;

        state.backups = Array.isArray(
            catalog.backups
        )
            ?
            catalog.backups
            :
            [];


        state.backups.sort(
            (a, b) => {
                const left = new Date(
                    backupDate(a) || 0
                ).getTime();

                const right = new Date(
                    backupDate(b) || 0
                ).getTime();

                return right - left;
            }
        );


        renderCapabilities();

        renderAutomation();

        renderRestoreState();

        renderStats();

        renderTable();
    };


    const refresh = async () => {
        const button = byId(
            "backup-refresh"
        );

        if (button) {
            button.disabled = true;
        }


        try {
            await loadData();
        }
        catch (error) {
            showToast(
                error.message
                ||
                "Impossible de charger les sauvegardes.",
                true
            );
        }
        finally {
            if (button) {
                button.disabled = false;
            }
        }
    };


    const createBackup = async () => {
        const button = byId(
            "backup-create"
        );

        button.disabled = true;

        const original = (
            button.querySelector("span")
            ?.textContent
            ||
            "Créer une sauvegarde"
        );


        if (button.querySelector("span")) {
            button.querySelector(
                "span"
            ).textContent = "Création en cours…";
        }


        try {
            const result = await fetchJson(
                "/api/backups",
                {
                    method: "POST",
                }
            );

            showToast(
                `Sauvegarde créée : ${
                    result.backup_id
                    ||
                    result.id
                    ||
                    "terminée"
                }`
            );

            await refresh();
        }
        catch (error) {
            showToast(
                error.message,
                true
            );
        }
        finally {
            button.disabled = false;

            if (button.querySelector("span")) {
                button.querySelector(
                    "span"
                ).textContent = original;
            }
        }
    };


    const findBackup = (id) => {
        return state.backups.find(
            (backup) => backupId(backup) === id
        );
    };


    const showDetails = (id) => {
        const backup = findBackup(
            id
        );

        if (!backup) {
            showToast(
                "Sauvegarde introuvable.",
                true
            );

            return;
        }


        const fields = [
            [
                "Identifiant",
                backupId(backup),
            ],
            [
                "Type",
                translateType(
                    pick(
                        backup,
                        [
                            "backup_type",
                            "type",
                        ],
                        "—"
                    )
                ),
            ],
            [
                "Date",
                formatDate(
                    backupDate(backup)
                ),
            ],
            [
                "Version Phoenix",
                backupVersion(backup),
            ],
            [
                "État",
                translateStatus(
                    pick(
                        backup,
                        ["status"],
                        "—"
                    )
                ),
            ],
            [
                "Nombre de fichiers",
                pick(
                    backup,
                    ["file_count"],
                    "—"
                ),
            ],
            [
                "Taille",
                formatBytes(
                    pick(
                        backup,
                        [
                            "total_size_bytes",
                            "size_bytes",
                        ]
                    )
                ),
            ],
        ];


        byId(
            "backup-details-content"
        ).innerHTML = fields.map(
            ([label, value]) => `
                <div class="backup-detail-item">
                    <span>
                        ${escapeHtml(label)}
                    </span>
                    <strong>
                        ${escapeHtml(value)}
                    </strong>
                </div>
            `
        ).join("");


        byId(
            "backup-details-dialog"
        ).showModal();
    };


    const verifyBackup = async (id) => {
        try {
            const result = await fetchJson(
                `/api/backups/${encodeURIComponent(id)}/verify`,
                {
                    method: "POST",
                }
            );


            const status = document.querySelector(
                `[data-status-for="${CSS.escape(id)}"]`
            );


            if (status) {
                status.textContent = "Vérifiée";
                status.classList.add(
                    "is-valid"
                );
                status.classList.remove(
                    "is-invalid"
                );
            }


            showToast(
                result.success
                ?
                "Intégrité de la sauvegarde vérifiée."
                :
                "Vérification terminée."
            );
        }
        catch (error) {
            showToast(
                error.message,
                true
            );
        }
    };


    const migrateBackup = async (id) => {
        const confirmed = window.confirm(
            "Créer une copie migrée et compatible de cette sauvegarde ? L'original restera intact."
        );

        if (!confirmed) {
            return;
        }


        try {
            const result = await fetchJson(
                `/api/backups/${encodeURIComponent(id)}/migrate`,
                {
                    method: "POST",
                }
            );


            showToast(
                result.published
                ?
                "Sauvegarde migrée et publiée."
                :
                "Aucune migration nécessaire."
            );

            await refresh();
        }
        catch (error) {
            showToast(
                error.message,
                true
            );
        }
    };


    const openRestore = (id) => {
        if (
            !state.capabilities
            ||
            !state.capabilities.live_restore_enabled
        ) {
            showToast(
                "La restauration LIVE est actuellement verrouillée.",
                true
            );

            return;
        }


        state.selectedRestoreId = id;

        byId(
            "backup-restore-id"
        ).textContent = id;

        byId(
            "backup-restore-confirm"
        ).value = "";

        byId(
            "backup-restore-submit"
        ).disabled = true;

        byId(
            "backup-restore-dialog"
        ).showModal();

        byId(
            "backup-restore-confirm"
        ).focus();
    };


    const submitRestore = async () => {
        const id = state.selectedRestoreId;

        if (!id) {
            return;
        }


        const input = byId(
            "backup-restore-confirm"
        );


        if (input.value.trim() !== id) {
            return;
        }


        const button = byId(
            "backup-restore-submit"
        );

        button.disabled = true;


        try {
            const result = await fetchJson(
                `/api/backups/${encodeURIComponent(id)}/restore/prepare`,
                {
                    method: "POST",
                }
            );


            byId(
                "backup-restore-dialog"
            ).close();


            showToast(
                result.message
                ||
                "Restauration préparée."
            );

            await refresh();
        }
        catch (error) {
            showToast(
                error.message,
                true
            );

            button.disabled = false;
        }
    };


    const updateClock = () => {
        const clock = byId(
            "backup-clock"
        );

        if (!clock) {
            return;
        }

        clock.textContent = new Intl.DateTimeFormat(
            "fr-FR",
            {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            }
        ).format(
            new Date()
        );
    };


    document.addEventListener(
        "click",
        (event) => {
            const close = event.target.closest(
                "[data-close-dialog]"
            );

            if (close) {
                const dialog = byId(
                    close.dataset.closeDialog
                );

                if (dialog?.open) {
                    dialog.close();
                }

                return;
            }


            const action = event.target.closest(
                "[data-action]"
            );

            if (!action) {
                return;
            }


            const id = action.dataset.backupId;

            switch (action.dataset.action) {
                case "details":
                    showDetails(id);
                    break;

                case "verify":
                    verifyBackup(id);
                    break;

                case "migrate":
                    migrateBackup(id);
                    break;

                case "restore":
                    openRestore(id);
                    break;
            }
        }
    );


    byId(
        "backup-restore-confirm"
    )?.addEventListener(
        "input",
        (event) => {
            byId(
                "backup-restore-submit"
            ).disabled = (
                event.target.value.trim()
                !==
                state.selectedRestoreId
            );
        }
    );


    byId(
        "backup-restore-submit"
    )?.addEventListener(
        "click",
        submitRestore
    );


    byId(
        "backup-create"
    )?.addEventListener(
        "click",
        createBackup
    );


    byId(
        "backup-refresh"
    )?.addEventListener(
        "click",
        refresh
    );


    byId(
        "backup-fullscreen"
    )?.addEventListener(
        "click",
        async () => {
            try {
                if (!document.fullscreenElement) {
                    await document.documentElement.requestFullscreen();
                }
                else {
                    await document.exitFullscreen();
                }
            }
            catch {
                showToast(
                    "Le plein écran n'est pas disponible.",
                    true
                );
            }
        }
    );


    updateClock();

    window.setInterval(
        updateClock,
        1000
    );


    refresh();

})();
