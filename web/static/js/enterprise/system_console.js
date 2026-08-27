(() => {
    "use strict";


    const $ = id =>
        document.getElementById(id);


    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }


    function statusLabel(status) {
        const labels = {
            EN_LIGNE: "EN LIGNE",
            DISPONIBLE: "DISPONIBLE",
            INDISPONIBLE: "INDISPONIBLE",
            OPERATIONNEL: "OPÉRATIONNEL",
            ATTENTION: "ATTENTION",
        };

        return (
            labels[status] ||
            status ||
            "INCONNU"
        );
    }


    function statusClass(status) {
        if (
            status === "EN_LIGNE" ||
            status === "OPERATIONNEL"
        ) {
            return "online";
        }

        if (
            status === "DISPONIBLE"
        ) {
            return "available";
        }

        return "unavailable";
    }


    function formatDate(value) {
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
                    dateStyle: "medium",
                    timeStyle: "short",
                }
            )
            .format(date)
        );
    }


    function formatUptime(seconds) {
        seconds =
            Number(seconds || 0);

        const days =
            Math.floor(
                seconds / 86400
            );

        const hours =
            Math.floor(
                (seconds % 86400) / 3600
            );

        const minutes =
            Math.floor(
                (seconds % 3600) / 60
            );

        if (days > 0) {
            return `${days} j ${hours} h`;
        }

        if (hours > 0) {
            return `${hours} h ${minutes} min`;
        }

        return `${minutes} min`;
    }


    async function requestJson(url) {
        const response =
            await fetch(
                url,
                {
                    credentials:
                        "same-origin",
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
            window.location.href =
                "/login";

            throw new Error(
                "Session expirée."
            );
        }

        if (!response.ok) {
            throw new Error(
                data.message ||
                data.error ||
                `Erreur ${response.status}`
            );
        }

        return data;
    }


    function showToast(message) {
        const toast =
            $("system-toast");

        toast.textContent =
            message;

        toast.classList.remove(
            "hidden"
        );

        window.clearTimeout(
            showToast.timer
        );

        showToast.timer =
            window.setTimeout(
                () => {
                    toast.classList.add(
                        "hidden"
                    );
                },
                3500
            );
    }


    function updateClock() {
        $("system-clock")
            .textContent =
                new Intl.DateTimeFormat(
                    "fr-FR",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit",
                    }
                )
                .format(
                    new Date()
                );
    }


    async function loadSession() {
        const data =
            await requestJson(
                "/api/session/me"
            );

        $("system-session-name")
            .textContent =
                data.display_name ||
                data.username ||
                "Utilisateur";

        $("system-session-role")
            .textContent =
                data.role ||
                "—";

        const photo =
            $("system-session-photo");

        if (data.photo_url) {
            photo.src =
                data.photo_url;
        } else {
            photo.removeAttribute(
                "src"
            );
        }
    }


    function setStateBadge(
        element,
        status
    ) {
        element.textContent =
            statusLabel(status);

        element.className =
            `system-state ${statusClass(status)}`;
    }


    function renderGlobal(status) {
        const box =
            $("system-global-status");

        box.classList.remove(
            "loading",
            "operational",
            "attention",
            "unavailable"
        );

        let cssClass =
            "unavailable";

        if (
            status ===
            "OPERATIONNEL"
        ) {
            cssClass =
                "operational";
        }

        if (
            status ===
            "ATTENTION"
        ) {
            cssClass =
                "attention";
        }

        box.classList.add(
            cssClass
        );

        box.querySelector(
            "strong"
        ).textContent =
            statusLabel(status);
    }


    function renderKpis(data) {
        const machine =
            data.machine;

        const databases =
            data.databases;

        $("system-cpu")
            .textContent =
                `${machine.cpu.percent}%`;

        $("system-cpu-detail")
            .textContent =
                `${machine.cpu.logical_cores ?? "—"} cœur(s) logique(s)`;

        $("system-memory")
            .textContent =
                `${machine.memory.percent}%`;

        $("system-memory-detail")
            .textContent =
                `${machine.memory.used_gb} / ${machine.memory.total_gb} Go`;

        $("system-disk")
            .textContent =
                `${machine.disk.percent}%`;

        $("system-disk-detail")
            .textContent =
                `${machine.disk.free_gb} Go libres`;

        $("system-databases")
            .textContent =
                `${databases.online}/${databases.count}`;

        $("system-databases-detail")
            .textContent =
                databases.unavailable === 0
                    ? "Toutes accessibles"
                    : `${databases.unavailable} indisponible(s)`;
    }


    function renderRuntime(data) {
        setStateBadge(
            $("system-engine-status"),
            data.runtime.engine.status
        );

        setStateBadge(
            $("system-stream-status"),
            data.runtime.stream_service.status
        );

        setStateBadge(
            $("system-process-status"),
            data.process.status
        );

        $("system-process-detail")
            .textContent =
                data.process.pid
                    ? (
                        `PID ${data.process.pid} · ` +
                        `${data.process.memory_rss_mb} Mo · ` +
                        `${formatUptime(data.process.uptime_seconds)}`
                    )
                    : "Processus indisponible";
    }


    function renderComponents(data) {
        const labels = {
            camera_manager:
                [
                    "Camera Manager",
                    "Gestion des caméras"
                ],

            frame_hub:
                [
                    "Frame Hub",
                    "Distribution des images"
                ],

            stream_service:
                [
                    "Stream Service",
                    "Service de diffusion"
                ],

            detector:
                [
                    "Détecteur IA",
                    "Backend de détection"
                ],

            memory_manager:
                [
                    "Memory Manager",
                    "Mémoire opérationnelle véhicule"
                ],
        };

        const components =
            data.components.components ||
            {};

        const container =
            $("system-components");

        container.innerHTML =
            Object.entries(
                components
            )
            .map(
                ([key, component]) => {
                    const label =
                        labels[key] ||
                        [key, "Composant Phoenix"];

                    return `
                        <div class="system-status-row">

                            <div>
                                <strong>
                                    ${escapeHtml(label[0])}
                                </strong>

                                <span>
                                    ${escapeHtml(label[1])}
                                </span>
                            </div>

                            <span
                                class="system-state ${statusClass(component.status)}"
                            >
                                ${escapeHtml(statusLabel(component.status))}
                            </span>

                        </div>
                    `;
                }
            )
            .join("");
    }


    function renderDatabases(data) {
        const databases =
            data.databases.databases ||
            [];

        $("system-database-summary")
            .textContent =
                `${data.databases.online} accessible(s) · ${data.databases.unavailable} indisponible(s)`;

        const body =
            $("system-database-body");

        if (!databases.length) {
            body.innerHTML = `
                <tr>
                    <td
                        colspan="5"
                        class="system-empty"
                    >
                        Aucune base SQLite détectée.
                    </td>
                </tr>
            `;

            return;
        }

        body.innerHTML =
            databases.map(
                database => `
                    <tr>

                        <td>
                            ${escapeHtml(database.name)}
                        </td>

                        <td>
                            <span
                                class="system-state ${statusClass(database.status)}"
                            >
                                ${escapeHtml(statusLabel(database.status))}
                            </span>
                        </td>

                        <td>
                            ${escapeHtml(database.size_mb ?? "—")} Mo
                        </td>

                        <td>
                            ${escapeHtml(database.tables ?? "—")}
                        </td>

                        <td>
                            ${escapeHtml(formatDate(database.modified_at))}
                        </td>

                    </tr>
                `
            ).join("");
    }


    function infoItem(
        label,
        value
    ) {
        return `
            <div class="system-info-item">
                <span>
                    ${escapeHtml(label)}
                </span>

                <strong>
                    ${escapeHtml(value || "—")}
                </strong>
            </div>
        `;
    }


    function renderEnvironment(data) {
        const env =
            data.environment;

        $("system-environment")
            .innerHTML =
                [
                    infoItem(
                        "APPLICATION",
                        env.application
                    ),

                    infoItem(
                        "VERSION",
                        env.version
                    ),

                    infoItem(
                        "ÉDITION",
                        env.codename
                    ),

                    infoItem(
                        "PYTHON",
                        env.python
                    ),

                    infoItem(
                        "SYSTÈME",
                        `${env.operating_system} ${env.os_release}`
                    ),

                    infoItem(
                        "ARCHITECTURE",
                        env.architecture
                    ),

                    infoItem(
                        "HÔTE",
                        env.hostname
                    ),

                    infoItem(
                        "UPTIME MACHINE",
                        formatUptime(
                            data.machine.uptime_seconds
                        )
                    ),
                ]
                .join("");
    }


    function renderDirectories(data) {
        const labels = {
            data:
                "Données locales",

            outputs:
                "Exports / sorties",

            videos:
                "Sources vidéo",
        };

        const container =
            $("system-directories");

        container.innerHTML =
            Object.entries(
                data.directories || {}
            )
            .map(
                ([key, directory]) => `
                    <div class="system-status-row">

                        <div>

                            <strong>
                                ${escapeHtml(labels[key] || key)}
                            </strong>

                            <span>
                                ${escapeHtml(directory.path || "—")}
                            </span>

                        </div>

                        <span
                            class="system-state ${statusClass(directory.status)}"
                        >
                            ${escapeHtml(statusLabel(directory.status))}
                        </span>

                    </div>
                `
            )
            .join("");
    }


    function renderHealth(data) {
        renderGlobal(
            data.overall_status
        );

        renderKpis(data);
        renderRuntime(data);
        renderComponents(data);
        renderDatabases(data);
        renderEnvironment(data);
        renderDirectories(data);

        $("system-generated-at")
            .textContent =
                `Dernière mesure système : ${formatDate(data.generated_at)}`;
    }


    async function refreshHealth(
        notify = false
    ) {
        try {
            const data =
                await requestJson(
                    "/api/system/health"
                );

            renderHealth(data);

            if (notify) {
                showToast(
                    "État système actualisé."
                );
            }

        } catch (error) {
            renderGlobal(
                "INDISPONIBLE"
            );

            showToast(
                error.message
            );
        }
    }


    function bindEvents() {
        $("system-refresh")
            .addEventListener(
                "click",
                () => {
                    refreshHealth(
                        true
                    );
                }
            );

        $("system-fullscreen")
            .addEventListener(
                "click",
                async () => {
                    try {
                        if (
                            document.fullscreenElement
                        ) {
                            await document.exitFullscreen();
                        } else {
                            await document
                                .documentElement
                                .requestFullscreen();
                        }

                    } catch (_) {
                        showToast(
                            "Le plein écran n'est pas disponible."
                        );
                    }
                }
            );
    }


    async function boot() {
        updateClock();

        window.setInterval(
            updateClock,
            1000
        );

        bindEvents();

        try {
            await loadSession();
            await refreshHealth();

        } catch (error) {
            showToast(
                error.message
            );
        }


        /*
         * Actualisation volontairement modérée :
         * évite de solliciter inutilement la machine.
         */
        window.setInterval(
            () => {
                refreshHealth();
            },
            10000
        );
    }


    document.addEventListener(
        "DOMContentLoaded",
        boot
    );

})();
