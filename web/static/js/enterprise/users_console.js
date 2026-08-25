(() => {
    "use strict";

    const state = {
        users: [],
        capabilities: {},
        session: {},
        selectedUsername: null,
        selectedUser: null,
        permissions: [],
        audit: [],
        auditIntegrity: null,
        modalAction: null,
        requestSummary: {},
    };


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


    function normalized(value) {
        return String(value ?? "")
            .trim()
            .toLowerCase();
    }


    function displayName(user) {
        return (
            user.display_name ||
            [user.prenom, user.postnom, user.nom]
                .filter(Boolean)
                .join(" ") ||
            user.username ||
            "Utilisateur"
        );
    }


    function statusLabel(status) {
        const labels = {
            ACTIVE: "ACTIF",
            APPROVED: "À SÉCURISER",
            SUSPENDED: "SUSPENDU",
            DISABLED: "DÉSACTIVÉ",
            EXPIRED: "EXPIRÉ",
            PENDING: "EN ATTENTE",
        };

        return labels[status] || status || "INCONNU";
    }


    function statusClass(status) {
        return normalized(status);
    }


    function formatDate(value) {
        if (!value) {
            return "—";
        }

        const date = new Date(value);

        if (Number.isNaN(date.getTime())) {
            return escapeHtml(value);
        }

        return new Intl.DateTimeFormat(
            "fr-FR",
            {
                dateStyle: "medium",
                timeStyle: "short",
            }
        ).format(date);
    }


    function photoUrl(user) {
        return user.photo_url || "";
    }


    async function requestJson(
        url,
        options = {}
    ) {
        const response = await fetch(
            url,
            {
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    ...(options.headers || {}),
                },
                ...options,
            }
        );

        let data = {};

        try {
            data = await response.json();
        } catch (_) {
            data = {};
        }

        if (response.status === 401) {
            window.location.href = "/login";
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


    function showToast(
        message,
        timeout = 3300
    ) {
        const toast = $("users-toast");

        toast.textContent = message;
        toast.classList.remove("hidden");

        window.clearTimeout(
            showToast.timer
        );

        showToast.timer = window.setTimeout(
            () => {
                toast.classList.add(
                    "hidden"
                );
            },
            timeout
        );
    }


    function setRegistryStatus(
        mode,
        label
    ) {
        const box = $("users-registry-status");

        box.classList.remove(
            "loading",
            "online",
            "error"
        );

        box.classList.add(mode);

        box.querySelector("strong")
            .textContent = label;
    }


    function updateClock() {
        $("users-clock").textContent =
            new Intl.DateTimeFormat(
                "fr-FR",
                {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                }
            ).format(new Date());
    }


    async function loadSession() {
        const data = await requestJson(
            "/api/session/me"
        );

        state.session = data;

        $("users-session-name")
            .textContent =
                data.display_name ||
                data.username ||
                "Utilisateur";

        $("users-session-role")
            .textContent =
                data.role || "—";

        const photo = $(
            "users-session-photo"
        );

        if (data.photo_url) {
            photo.src = data.photo_url;
        } else {
            photo.removeAttribute("src");
        }
    }


    async function loadCapabilities() {
        const data = await requestJson(
            "/api/users/capabilities"
        );

        state.capabilities =
            data.capabilities || {};

        $("users-account-requests")
            .classList.toggle(
                "hidden",
                !state.capabilities
                    .approve_request
            );
    }


    async function loadRequestSummary() {
        const button =
            $("users-account-requests");

        const badge =
            $("users-request-count");


        if (
            !state.capabilities
                .approve_request
        ) {
            button.classList.add(
                "hidden"
            );

            badge.classList.add(
                "hidden"
            );

            return;
        }


        try {
            const data =
                await requestJson(
                    "/api/users/account-requests/summary"
                );


            state.requestSummary =
                data.summary || {};


            const pending =
                Number(
                    state.requestSummary
                        .pending ||
                    0
                );


            badge.textContent =
                String(
                    pending
                );


            badge.classList.toggle(
                "hidden",
                pending <= 0
            );


            button.title =
                pending > 0
                    ? `${pending} demande${pending > 1 ? "s" : ""} en attente`
                    : "Aucune demande de compte en attente";

        } catch (_) {
            badge.classList.add(
                "hidden"
            );
        }
    }


    async function loadUsers() {
        setRegistryStatus(
            "loading",
            "CONNEXION"
        );

        const data = await requestJson(
            "/api/users"
        );

        state.users =
            Array.isArray(data.users)
                ? data.users
                : [];

        renderSiteFilter();
        renderKpis();
        renderUsers();

        setRegistryStatus(
            "online",
            "EN LIGNE"
        );
    }


    function renderSiteFilter() {
        const select = $(
            "users-filter-site"
        );

        const previous =
            select.value;

        const sites = [
            ...new Set(
                state.users
                    .map(
                        user =>
                            String(
                                user.site_affectation ||
                                ""
                            ).trim()
                    )
                    .filter(Boolean)
            ),
        ].sort(
            (a, b) =>
                a.localeCompare(
                    b,
                    "fr"
                )
        );

        select.innerHTML =
            '<option value="">Tous les sites</option>' +
            sites.map(
                site =>
                    `<option value="${escapeHtml(site)}">${escapeHtml(site)}</option>`
            ).join("");

        select.value = previous;
    }


    function renderKpis() {
        const total =
            state.users.length;

        const active =
            state.users.filter(
                user =>
                    user.status ===
                    "ACTIVE"
            ).length;

        const approved =
            state.users.filter(
                user =>
                    user.status ===
                    "APPROVED"
            ).length;

        const restricted =
            state.users.filter(
                user =>
                    [
                        "SUSPENDED",
                        "DISABLED",
                        "EXPIRED",
                    ].includes(
                        user.status
                    )
            ).length;

        $("users-kpi-total")
            .textContent = total;

        $("users-kpi-active")
            .textContent = active;

        $("users-kpi-approved")
            .textContent = approved;

        $("users-kpi-restricted")
            .textContent = restricted;
    }


    function filteredUsers() {
        const query =
            normalized(
                $("users-search").value
            );

        const role =
            $("users-filter-role").value;

        const status =
            $("users-filter-status").value;

        const site =
            $("users-filter-site").value;

        return state.users.filter(
            user => {
                if (
                    role &&
                    user.role !== role
                ) {
                    return false;
                }

                if (
                    status &&
                    user.status !== status
                ) {
                    return false;
                }

                if (
                    site &&
                    user.site_affectation !== site
                ) {
                    return false;
                }

                if (!query) {
                    return true;
                }

                const haystack = [
                    user.display_name,
                    user.nom,
                    user.postnom,
                    user.prenom,
                    user.username,
                    user.organisation,
                    user.departement,
                    user.fonction,
                    user.site_affectation,
                    user.role,
                    user.status,
                ]
                    .map(normalized)
                    .join(" ");

                return haystack.includes(
                    query
                );
            }
        );
    }


    function renderUsers() {
        const users =
            filteredUsers();

        const body = $(
            "users-table-body"
        );

        $("users-visible-count")
            .textContent =
                `${users.length} résultat${
                    users.length > 1
                        ? "s"
                        : ""
                }`;

        if (!users.length) {
            body.innerHTML = `
                <tr>
                    <td
                        colspan="6"
                        class="users-empty-cell"
                    >
                        Aucun utilisateur ne correspond aux filtres.
                    </td>
                </tr>
            `;

            return;
        }

        body.innerHTML =
            users.map(
                user => {
                    const selected =
                        user.username ===
                        state.selectedUsername;

                    const photo =
                        photoUrl(user);

                    return `
                        <tr
                            class="users-row ${selected ? "selected" : ""}"
                            data-username="${escapeHtml(user.username)}"
                        >
                            <td>
                                <div class="users-identity">

                                    <img
                                        class="users-avatar"
                                        src="${escapeHtml(photo)}"
                                        alt=""
                                    >

                                    <div>
                                        <strong>
                                            ${escapeHtml(displayName(user))}
                                        </strong>

                                        <small>
                                            ${escapeHtml(user.fonction || user.departement || "—")}
                                        </small>
                                    </div>

                                </div>
                            </td>

                            <td>
                                ${escapeHtml(user.username || "—")}
                            </td>

                            <td>
                                <span class="users-role-badge">
                                    ${escapeHtml(user.role || "—")}
                                </span>
                            </td>

                            <td>
                                ${escapeHtml(user.site_affectation || "—")}
                            </td>

                            <td>
                                <span class="users-status-badge ${statusClass(user.status)}">
                                    ${escapeHtml(statusLabel(user.status))}
                                </span>
                            </td>

                            <td>
                                ${formatDate(user.last_login_at)}
                            </td>
                        </tr>
                    `;
                }
            ).join("");

        body.querySelectorAll(
            ".users-row"
        ).forEach(
            row => {
                row.addEventListener(
                    "click",
                    () => {
                        selectUser(
                            row.dataset.username
                        );
                    }
                );
            }
        );
    }


    async function selectUser(
        username
    ) {
        state.selectedUsername =
            username;

        renderUsers();

        const panel = $(
            "users-detail-panel"
        );

        panel.innerHTML = `
            <div class="users-detail-empty">
                <strong>
                    CHARGEMENT DU DOSSIER
                </strong>
            </div>
        `;

        try {
            const details =
                await requestJson(
                    `/api/users/${encodeURIComponent(username)}`
                );

            state.selectedUser =
                details.user;

            state.permissions =
                details.effective_permissions ||
                [];

            state.audit = [];
            state.auditIntegrity = null;

            if (
                state.capabilities
                    .view_audit
            ) {
                const audit =
                    await requestJson(
                        `/api/users/${encodeURIComponent(username)}/audit`
                    );

                state.audit =
                    audit.events || [];

                state.auditIntegrity =
                    audit.integrity_valid;
            }

            renderDetail();

        } catch (error) {
            panel.innerHTML = `
                <div class="users-detail-empty">
                    <strong>
                        DOSSIER INDISPONIBLE
                    </strong>
                    <p>
                        ${escapeHtml(error.message)}
                    </p>
                </div>
            `;
        }
    }


    function infoItem(
        label,
        value
    ) {
        return `
            <div class="users-info-item">
                <span>${escapeHtml(label)}</span>
                <strong>${escapeHtml(value || "—")}</strong>
            </div>
        `;
    }


    function actionButton(
        action,
        label,
        icon,
        danger = false
    ) {
        return `
            <button
                class="users-action-button ${danger ? "danger" : ""}"
                type="button"
                data-user-action="${escapeHtml(action)}"
            >
                <svg class="phoenix-icon">
                    <use href="/static/icons/phoenix-ui.svg#${escapeHtml(icon)}"></use>
                </svg>

                ${escapeHtml(label)}
            </button>
        `;
    }


    function renderDetail() {
        const user =
            state.selectedUser;

        if (!user) {
            return;
        }

        const isSelf =
            normalized(user.username) ===
            normalized(state.session.username);

        const isAdmin =
            user.role === "ADMIN";

        let actions = "";

        if (
            state.capabilities.print
        ) {
            actions += actionButton(
                "print",
                "Imprimer la fiche",
                "icon-print"
            );
        }

        if (
            state.capabilities.edit
        ) {
            actions += actionButton(
                "edit",
                "Modifier",
                "icon-edit"
            );
        }

        if (
            state.capabilities.suspend &&
            !isSelf &&
            !isAdmin &&
            user.status !== "SUSPENDED"
        ) {
            actions += actionButton(
                "suspend",
                "Suspendre",
                "icon-suspend",
                true
            );
        }

        if (
            state.capabilities.disable &&
            !isSelf &&
            !isAdmin &&
            user.status !== "DISABLED"
        ) {
            actions += actionButton(
                "disable",
                "Désactiver",
                "icon-disable",
                true
            );
        }

        if (
            state.capabilities.reactivate &&
            !isAdmin &&
            [
                "SUSPENDED",
                "DISABLED",
                "EXPIRED",
            ].includes(
                user.status
            )
        ) {
            actions += actionButton(
                "reactivate",
                "Réactiver",
                "icon-refresh-user"
            );
        }

        if (
            state.capabilities.change_role &&
            !isSelf &&
            !isAdmin
        ) {
            actions += actionButton(
                "role",
                "Modifier le rôle",
                "icon-role"
            );
        }

        const sensitive = [];

        if (
            Object.prototype
                .hasOwnProperty
                .call(
                    user,
                    "email"
                )
        ) {
            sensitive.push(
                infoItem(
                    "E-MAIL",
                    user.email
                )
            );
        }

        if (
            Object.prototype
                .hasOwnProperty
                .call(
                    user,
                    "telephone"
                )
        ) {
            sensitive.push(
                infoItem(
                    "TÉLÉPHONE",
                    user.telephone
                )
            );
        }

        if (
            Object.prototype
                .hasOwnProperty
                .call(
                    user,
                    "matricule"
                )
        ) {
            sensitive.push(
                infoItem(
                    "MATRICULE",
                    user.matricule
                )
            );
        }

        const permissionHtml =
            state.permissions.length
                ? state.permissions.map(
                    item => `
                        <span
                            class="users-permission-chip"
                            title="${escapeHtml(item.permission)}"
                        >
                            ${escapeHtml(item.label)}
                        </span>
                    `
                ).join("")
                : `
                    <span class="users-permission-chip">
                        Aucun droit opérationnel catalogué
                    </span>
                `;

        const auditHtml =
            state.audit.length
                ? state.audit
                    .slice(0, 12)
                    .map(
                        event => `
                            <div class="users-audit-event">
                                <strong>
                                    ${escapeHtml(event.action)}
                                </strong>

                                <span>
                                    ${formatDate(event.created_at)}
                                    ·
                                    ${escapeHtml(event.actor_username || "SYSTEM")}
                                </span>

                                ${
                                    event.reason
                                        ? `
                                            <span>
                                                ${escapeHtml(event.reason)}
                                            </span>
                                        `
                                        : ""
                                }
                            </div>
                        `
                    ).join("")
                : `
                    <div class="users-audit-event">
                        <span>
                            Aucun événement administratif accessible.
                        </span>
                    </div>
                `;

        $("users-detail-panel")
            .innerHTML = `

                <div class="users-profile-header">

                    <div class="users-profile-main">

                        <img
                            class="users-avatar"
                            src="${escapeHtml(photoUrl(user))}"
                            alt=""
                        >

                        <div>

                            <h2>
                                ${escapeHtml(displayName(user))}
                            </h2>

                            <p>
                                ${escapeHtml(user.username)}
                            </p>

                            <div class="users-profile-badges">

                                <span class="users-role-badge">
                                    ${escapeHtml(user.role)}
                                </span>

                                <span class="users-status-badge ${statusClass(user.status)}">
                                    ${escapeHtml(statusLabel(user.status))}
                                </span>

                            </div>

                        </div>

                    </div>

                </div>


                <section class="users-detail-section">

                    <h3>
                        DOSSIER PROFESSIONNEL
                    </h3>

                    <div class="users-info-grid">

                        ${infoItem("ORGANISATION", user.organisation)}
                        ${infoItem("DÉPARTEMENT", user.departement)}
                        ${infoItem("FONCTION", user.fonction)}
                        ${infoItem("SITE", user.site_affectation)}
                        ${infoItem("RESPONSABLE", user.responsable)}
                        ${infoItem("EXPIRATION", user.account_expiry)}

                        ${sensitive.join("")}

                    </div>

                </section>


                <section class="users-detail-section">

                    <h3>
                        SÉCURITÉ DU COMPTE
                    </h3>

                    <div class="users-info-grid">

                        ${infoItem("STATUT", statusLabel(user.status))}
                        ${infoItem("DERNIÈRE CONNEXION", formatDate(user.last_login_at))}
                        ${infoItem("APPROBATION", formatDate(user.approved_at))}
                        ${infoItem("APPROUVÉ PAR", user.approved_by)}
                        ${infoItem(
                            "MOT DE PASSE TEMPORAIRE",
                            user.must_change_password
                                ? "OUI"
                                : "NON"
                        )}
                        ${infoItem("RÉVISION DOSSIER", user.revision)}

                    </div>

                </section>


                <section class="users-detail-section">

                    <h3>
                        DROITS EFFECTIFS
                    </h3>

                    <div class="users-permissions">
                        ${permissionHtml}
                    </div>

                </section>


                ${
                    actions
                        ? `
                            <section class="users-detail-section">

                                <h3>
                                    ACTIONS AUTORISÉES
                                </h3>

                                <div class="users-actions">
                                    ${actions}
                                </div>

                            </section>
                        `
                        : ""
                }


                ${
                    state.capabilities.view_audit
                        ? `
                            <section class="users-detail-section">

                                <h3>
                                    HISTORIQUE ADMINISTRATIF
                                </h3>

                                <div class="users-integrity">
                                    Intégrité du journal :
                                    ${
                                        state.auditIntegrity
                                            ? "VALIDÉE"
                                            : "À VÉRIFIER"
                                    }
                                </div>

                                <div class="users-audit-list">
                                    ${auditHtml}
                                </div>

                            </section>
                        `
                        : ""
                }
            `;

        document
            .querySelectorAll(
                "[data-user-action]"
            )
            .forEach(
                button => {
                    button.addEventListener(
                        "click",
                        () => {
                            const action =
                                button.dataset.userAction;


                            if (
                                action ===
                                "print"
                            ) {
                                window.open(
                                    `/users/${encodeURIComponent(user.username)}/print`,
                                    "_blank",
                                    "noopener"
                                );

                                return;
                            }


                            openModal(
                                action
                            );
                        }
                    );
                }
            );
    }


    function modalField(
        key,
        label,
        value,
        type = "text"
    ) {
        return `
            <div class="users-field">
                <label for="modal-${escapeHtml(key)}">
                    ${escapeHtml(label)}
                </label>

                <input
                    id="modal-${escapeHtml(key)}"
                    name="${escapeHtml(key)}"
                    type="${escapeHtml(type)}"
                    value="${escapeHtml(value || "")}"
                >
            </div>
        `;
    }


    function openModal(
        action
    ) {
        const user =
            state.selectedUser;

        if (!user) {
            return;
        }

        state.modalAction = action;

        const title =
            $("users-modal-title");

        const body =
            $("users-modal-body");

        const submit =
            $("users-modal-submit");

        if (action === "edit") {
            title.textContent =
                "Modifier le dossier";

            submit.textContent =
                "Enregistrer";

            body.innerHTML = `
                <div class="users-form-grid">
                    ${modalField("nom", "Nom", user.nom)}
                    ${modalField("postnom", "Postnom", user.postnom)}
                    ${modalField("prenom", "Prénom", user.prenom)}
                    ${modalField("email", "E-mail", user.email, "email")}
                    ${modalField("telephone", "Téléphone", user.telephone)}
                    ${modalField("organisation", "Organisation", user.organisation)}
                    ${modalField("departement", "Département", user.departement)}
                    ${modalField("fonction", "Fonction", user.fonction)}
                    ${modalField("site_affectation", "Site d'affectation", user.site_affectation)}
                    ${modalField("responsable", "Responsable", user.responsable)}
                    ${modalField("account_expiry", "Expiration du compte", user.account_expiry)}
                </div>
            `;
        }

        if (action === "role") {
            title.textContent =
                "Modifier le rôle";

            submit.textContent =
                "Appliquer le nouveau rôle";

            const roles =
                (
                    state.capabilities
                        .assignable_roles ||
                    []
                )
                .filter(
                    role =>
                        role !== user.role
                );

            body.innerHTML = `
                <p class="users-modal-note">
                    La promotion vers ADMIN est volontairement
                    interdite depuis Phoenix Vision AI.
                    La session de l'utilisateur sera révoquée
                    après le changement de rôle.
                </p>

                <div class="users-field">
                    <label>Nouveau rôle</label>

                    <select name="role" required>
                        ${roles.map(
                            role =>
                                `<option value="${escapeHtml(role)}">${escapeHtml(role)}</option>`
                        ).join("")}
                    </select>
                </div>

                <div class="users-field full">
                    <label>Motif obligatoire</label>
                    <textarea name="reason" required></textarea>
                </div>
            `;
        }

        if (
            [
                "suspend",
                "disable",
                "reactivate",
            ].includes(action)
        ) {
            const labels = {
                suspend:
                    "Suspendre le compte",
                disable:
                    "Désactiver le compte",
                reactivate:
                    "Réactiver le compte",
            };

            title.textContent =
                labels[action];

            submit.textContent =
                "Confirmer l'action";

            body.innerHTML = `
                <p class="users-modal-note">
                    Utilisateur :
                    <strong>
                        ${escapeHtml(displayName(user))}
                    </strong>
                    ·
                    ${escapeHtml(user.username)}
                </p>

                <div class="users-field full">
                    <label>
                        Motif obligatoire
                    </label>

                    <textarea
                        name="reason"
                        required
                        minlength="3"
                    ></textarea>
                </div>
            `;
        }

        const modal =
            $("users-modal");

        modal.classList.remove(
            "hidden"
        );

        modal.setAttribute(
            "aria-hidden",
            "false"
        );
    }


    function closeModal() {
        const modal =
            $("users-modal");

        modal.classList.add(
            "hidden"
        );

        modal.setAttribute(
            "aria-hidden",
            "true"
        );

        state.modalAction = null;
    }


    async function submitModal(
        event
    ) {
        event.preventDefault();

        const user =
            state.selectedUser;

        const action =
            state.modalAction;

        if (
            !user ||
            !action
        ) {
            return;
        }

        const form =
            event.currentTarget;

        const formData =
            new FormData(form);

        const payload =
            Object.fromEntries(
                formData.entries()
            );

        const submit =
            $("users-modal-submit");

        submit.disabled = true;

        try {
            if (action === "edit") {
                await requestJson(
                    `/api/users/${encodeURIComponent(user.username)}`,
                    {
                        method: "PATCH",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );
            }

            if (action === "suspend") {
                await requestJson(
                    `/api/users/${encodeURIComponent(user.username)}/suspend`,
                    {
                        method: "POST",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );
            }

            if (action === "disable") {
                await requestJson(
                    `/api/users/${encodeURIComponent(user.username)}/disable`,
                    {
                        method: "POST",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );
            }

            if (action === "reactivate") {
                await requestJson(
                    `/api/users/${encodeURIComponent(user.username)}/reactivate`,
                    {
                        method: "POST",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );
            }

            if (action === "role") {
                await requestJson(
                    `/api/users/${encodeURIComponent(user.username)}/role`,
                    {
                        method: "POST",
                        body: JSON.stringify(
                            payload
                        ),
                    }
                );
            }

            closeModal();

            showToast(
                "Dossier utilisateur mis à jour."
            );

            const username =
                user.username;

            await loadUsers();

            await selectUser(
                username
            );

        } catch (error) {
            showToast(
                error.message,
                5000
            );

        } finally {
            submit.disabled = false;
        }
    }


    async function refresh() {
        try {
            await loadUsers();
            await loadRequestSummary();

            if (
                state.selectedUsername
            ) {
                await selectUser(
                    state.selectedUsername
                );
            }

        } catch (error) {
            setRegistryStatus(
                "error",
                "INDISPONIBLE"
            );

            showToast(
                error.message,
                5000
            );
        }
    }


    function bindEvents() {
        [
            "users-search",
            "users-filter-role",
            "users-filter-status",
            "users-filter-site",
        ].forEach(
            id => {
                $(id).addEventListener(
                    id === "users-search"
                        ? "input"
                        : "change",
                    renderUsers
                );
            }
        );

        $("users-refresh")
            .addEventListener(
                "click",
                refresh
            );

        $("users-fullscreen")
            .addEventListener(
                "click",
                async () => {
                    try {
                        if (
                            document.fullscreenElement
                        ) {
                            await document.exitFullscreen();
                        } else {
                            await document.documentElement
                                .requestFullscreen();
                        }
                    } catch (_) {
                        showToast(
                            "Le mode plein écran n'est pas disponible."
                        );
                    }
                }
            );

        $("users-modal-close")
            .addEventListener(
                "click",
                closeModal
            );

        $("users-modal-cancel")
            .addEventListener(
                "click",
                closeModal
            );

        document
            .querySelector(
                ".users-modal-backdrop"
            )
            .addEventListener(
                "click",
                closeModal
            );

        $("users-modal-form")
            .addEventListener(
                "submit",
                submitModal
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
            await loadCapabilities();
            await loadUsers();
            await loadRequestSummary();

        } catch (error) {
            setRegistryStatus(
                "error",
                "INDISPONIBLE"
            );

            showToast(
                error.message,
                5000
            );
        }
    }


    document.addEventListener(
        "DOMContentLoaded",
        boot
    );

})();
