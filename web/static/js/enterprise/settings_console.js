"use strict";


document.addEventListener(
    "DOMContentLoaded",
    () => {


        const state = {

            settings: [],

            capabilities: {},

            installation: null,

            permissions: null,

            matrix: null,

            audit: null,

            languages: null,

        };


        const byId = (
            id
        ) => document.getElementById(
            id
        );


        const labels = {

            "general.site_name":
                "Nom du site",

            "general.country_code":
                "Pays",

            "general.city":
                "Ville",

            "general.timezone":
                "Fuseau horaire",

            "interface.default_language":
                "Langue par défaut",

            "interface.date_format":
                "Format de date",

            "interface.time_format":
                "Format de l'heure",

            "interface.theme":
                "Thème",

            "operations.confirm_sensitive_actions":
                "Confirmer les actions sensibles",

            "anpr.review_uncertain_reads":
                "Vérification des lectures incertaines",

            "anpr.show_confidence":
                "Afficher la confiance LAPI",

            "reports.default_period":
                "Période par défaut",

            "reports.default_sections":
                "Sections par défaut",

            "reports.paper_format":
                "Format papier",

            "reports.include_integrity":
                "Informations d'intégrité",

            "installation.product_name":
                "Produit",

            "installation.software_version":
                "Version",

            "installation.codename":
                "Édition / génération",

            "installation.publisher":
                "Éditeur",

            "installation.license_name":
                "Licence",

        };


        const permissionLabels = {

            "settings.view":
                "Consulter les paramètres",

            "settings.view_installation":
                "Voir les informations d'installation",

            "settings.permissions.view_self":
                "Voir mes autorisations",

            "settings.permissions.view_matrix":
                "Voir la matrice des rôles",

            "settings.update_general":
                "Modifier les paramètres généraux",

            "settings.update_interface":
                "Modifier l'interface globale",

            "settings.update_operations":
                "Modifier les paramètres d'exploitation",

            "settings.update_anpr":
                "Modifier les paramètres LAPI",

            "settings.update_reports":
                "Modifier les paramètres Rapports",

            "settings.audit.view":
                "Consulter le journal des paramètres",

            "reports.view":
                "Consulter les rapports",

            "reports.generate":
                "Générer des rapports",

            "reports.print":
                "Imprimer des rapports",

            "reports.export_pdf":
                "Exporter les rapports PDF",

            "anpr.view":
                "Consulter LAPI",

            "anpr.search":
                "Rechercher une plaque",

            "history.view":
                "Consulter l'historique",

            "history.print":
                "Imprimer l'historique",

            "watchlist.view":
                "Consulter la surveillance",

            "watchlist.propose":
                "Proposer une surveillance",

            "watchlist.approve_local":
                "Valider une surveillance locale",

            "watchlist.match":
                "Détecter une correspondance",

            "evidence.view":
                "Consulter les preuves",

            "evidence.print":
                "Imprimer les preuves",

            "evidence.export_video":
                "Exporter une vidéo de preuve",

        };


        function permissionLabel(
            permission
        ) {

            return (
                permissionLabels[
                    permission
                ]
                ||
                permission
            );

        }


        function showMessage(
            text,
            type=""
        ) {

            const element = byId(
                "settings-message"
            );


            if (!element) {

                return;

            }


            element.textContent =
                text;


            element.className =
                (
                    "settings-message "
                    +
                    type
                ).trim();


            element.hidden =
                false;


            window.setTimeout(
                () => {

                    element.hidden =
                        true;

                },
                4500
            );

        }


        async function requestJson(
            url,
            options={}
        ) {

            const response = await fetch(
                url,
                {
                    credentials:
                        "same-origin",

                    ...options,
                }
            );


            let data = null;


            try {

                data = await response.json();

            }
            catch {

                data = null;

            }


            if (!response.ok) {

                const error =
                    new Error(
                        (
                            data
                            &&
                            (
                                data.message
                                ||
                                data.error
                            )
                        )
                        ||
                        (
                            "Erreur HTTP "
                            +
                            response.status
                        )
                    );


                error.status =
                    response.status;


                throw error;

            }


            return data;

        }


        async function optionalRequestJson(
            url
        ) {

            try {

                return await requestJson(
                    url
                );

            }
            catch (error) {

                console.warn(
                    (
                        "Phoenix Vision AI : "
                        +
                        "service secondaire indisponible : "
                        +
                        url
                    ),
                    error
                );

                return null;

            }

        }


        function activateView(
            view
        ) {

            document
                .querySelectorAll(
                    ".settings-section-link"
                )
                .forEach(
                    button => {

                        button.classList.toggle(
                            "active",
                            button.dataset.section
                            ===
                            view
                        );

                    }
                );


            document
                .querySelectorAll(
                    ".settings-view"
                )
                .forEach(
                    section => {

                        section.classList.toggle(
                            "active",
                            section.dataset.settingsView
                            ===
                            view
                        );

                    }
                );

        }


        document
            .querySelectorAll(
                ".settings-section-link"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            activateView(
                                button.dataset.section
                            );

                        }
                    );

                }
            );


        function settingLabel(
            setting
        ) {

            return (
                labels[
                    setting.key
                ]
                ||
                setting.key
            );

        }


        function formatValue(
            value
        ) {

            if (
                value === null
                ||
                value === undefined
                ||
                value === ""
            ) {

                return "NON CONFIGURÉ";

            }


            if (
                value === true
            ) {

                return "ACTIVÉ";

            }


            if (
                value === false
            ) {

                return "DÉSACTIVÉ";

            }


            if (
                Array.isArray(
                    value
                )
            ) {

                return value.join(
                    ", "
                );

            }


            return String(
                value
            );

        }


        function createSelect(
            setting,
            options
        ) {

            const select =
                document.createElement(
                    "select"
                );


            select.className =
                "phx-input";


            select.dataset.settingKey =
                setting.key;


            options.forEach(
                option => {

                    const element =
                        document.createElement(
                            "option"
                        );


                    element.value =
                        option.value;


                    element.textContent =
                        option.label;


                    if (
                        String(
                            setting.value
                        )
                        ===
                        String(
                            option.value
                        )
                    ) {

                        element.selected =
                            true;

                    }


                    if (
                        option.disabled
                    ) {

                        element.disabled =
                            true;

                    }


                    select.appendChild(
                        element
                    );

                }
            );


            return select;

        }


        function createListControl(
            setting
        ) {

            const wrapper =
                document.createElement(
                    "div"
                );


            wrapper.className =
                "settings-report-sections";


            const options = [

                [
                    "summary",
                    "Synthèse"
                ],

                [
                    "vehicles",
                    "Véhicules"
                ],

                [
                    "events",
                    "Événements"
                ],

                [
                    "alerts",
                    "Alertes"
                ],

                [
                    "anpr",
                    "Plaques / LAPI"
                ],

                [
                    "watchlist",
                    "Surveillance"
                ],

            ];


            options.forEach(
                (
                    [
                        value,
                        label
                    ]
                ) => {

                    const item =
                        document.createElement(
                            "label"
                        );


                    const input =
                        document.createElement(
                            "input"
                        );


                    input.type =
                        "checkbox";


                    input.value =
                        value;


                    input.checked =
                        Array.isArray(
                            setting.value
                        )
                        &&
                        setting.value.includes(
                            value
                        );


                    input.dataset.settingKey =
                        setting.key;


                    item.appendChild(
                        input
                    );


                    item.appendChild(
                        document.createTextNode(
                            label
                        )
                    );


                    wrapper.appendChild(
                        item
                    );

                }
            );


            return wrapper;

        }


        function createControl(
            setting
        ) {

            if (
                !setting.can_update
            ) {

                const readonly =
                    document.createElement(
                        "div"
                    );


                readonly.className =
                    "settings-readonly-value";


                const value =
                    document.createElement(
                        "span"
                    );


                value.textContent =
                    formatValue(
                        setting.value
                    );


                const badge =
                    document.createElement(
                        "span"
                    );


                badge.className =
                    "phx-status";


                badge.textContent =
                    "LECTURE SEULE";


                readonly.append(
                    value,
                    badge
                );


                return readonly;

            }


            if (
                setting.key
                ===
                "interface.default_language"
            ) {

                const registry =
                    (
                        state.languages
                        &&
                        Array.isArray(
                            state.languages.languages
                        )
                    )
                    ?
                    state.languages.languages
                    :
                    [];


                const options =
                    registry.map(
                        locale => {

                            const unavailable =
                                !locale.selectable;


                            return {
                                value:
                                    locale.code,

                                label:
                                    (
                                        locale.native_name
                                        +
                                        (
                                            unavailable
                                            ?
                                            " — bientôt disponible"
                                            :
                                            ""
                                        )
                                    ),

                                disabled:
                                    (
                                        unavailable
                                        &&
                                        setting.value
                                        !==
                                        locale.code
                                    ),
                            };

                        }
                    );


                return createSelect(
                    setting,
                    options
                );

            }


            if (
                setting.key
                ===
                "interface.date_format"
            ) {

                return createSelect(
                    setting,
                    [
                        {
                            value:
                                "DD/MM/YYYY",

                            label:
                                "JJ/MM/AAAA",
                        },

                        {
                            value:
                                "YYYY-MM-DD",

                            label:
                                "AAAA-MM-JJ",
                        },
                    ]
                );

            }


            if (
                setting.key
                ===
                "interface.time_format"
            ) {

                return createSelect(
                    setting,
                    [
                        {
                            value:
                                "24h",

                            label:
                                "24 heures",
                        },

                        {
                            value:
                                "12h",

                            label:
                                "12 heures",
                        },
                    ]
                );

            }


            if (
                setting.key
                ===
                "reports.default_period"
            ) {

                return createSelect(
                    setting,
                    [
                        {
                            value:
                                "today",

                            label:
                                "Aujourd'hui",
                        },

                        {
                            value:
                                "yesterday",

                            label:
                                "Hier",
                        },

                        {
                            value:
                                "week",

                            label:
                                "Cette semaine",
                        },

                        {
                            value:
                                "previous_week",

                            label:
                                "Semaine précédente",
                        },

                        {
                            value:
                                "month",

                            label:
                                "Ce mois",
                        },

                        {
                            value:
                                "previous_month",

                            label:
                                "Mois précédent",
                        },

                        {
                            value:
                                "quarter",

                            label:
                                "Ce trimestre",
                        },

                        {
                            value:
                                "semester",

                            label:
                                "Ce semestre",
                        },

                        {
                            value:
                                "year",

                            label:
                                "Cette année",
                        },
                    ]
                );

            }


            if (
                setting.key
                ===
                "reports.default_sections"
            ) {

                return createListControl(
                    setting
                );

            }


            if (
                setting.data_type
                ===
                "boolean"
            ) {

                const wrapper =
                    document.createElement(
                        "label"
                    );


                wrapper.className =
                    "settings-toggle";


                const text =
                    document.createElement(
                        "span"
                    );


                text.textContent =
                    (
                        setting.value
                        ?
                        "Activé"
                        :
                        "Désactivé"
                    );


                const input =
                    document.createElement(
                        "input"
                    );


                input.type =
                    "checkbox";


                input.checked =
                    Boolean(
                        setting.value
                    );


                input.dataset.settingKey =
                    setting.key;


                input.addEventListener(
                    "change",
                    () => {

                        text.textContent =
                            (
                                input.checked
                                ?
                                "Activé"
                                :
                                "Désactivé"
                            );

                    }
                );


                wrapper.append(
                    text,
                    input
                );


                return wrapper;

            }


            const input =
                document.createElement(
                    "input"
                );


            input.type =
                "text";


            input.className =
                "phx-input";


            input.value =
                (
                    setting.value
                    ??
                    ""
                );


            input.dataset.settingKey =
                setting.key;


            return input;

        }


        function renderCategories() {

            const categories = [
                "GENERAL",
                "INTERFACE",
                "OPERATIONS",
                "ANPR",
                "REPORTS",
            ];


            categories.forEach(
                category => {

                    const container =
                        document.querySelector(
                            (
                                '[data-settings-category="'
                                +
                                category
                                +
                                '"]'
                            )
                        );


                    if (!container) {

                        return;

                    }


                    container.innerHTML =
                        "";


                    const settings =
                        state.settings.filter(
                            item =>
                                item.category
                                ===
                                category
                        );


                    let editable =
                        false;


                    settings.forEach(
                        setting => {

                            const card =
                                document.createElement(
                                    "article"
                                );


                            card.className =
                                "settings-field-card";


                            const info =
                                document.createElement(
                                    "div"
                                );


                            info.className =
                                "settings-field-info";


                            const title =
                                document.createElement(
                                    "strong"
                                );


                            title.textContent =
                                settingLabel(
                                    setting
                                );


                            const description =
                                document.createElement(
                                    "p"
                                );


                            description.textContent =
                                (
                                    setting.description
                                    ||
                                    ""
                                );


                            const meta =
                                document.createElement(
                                    "div"
                                );


                            meta.className =
                                "settings-field-meta";


                            const revision =
                                document.createElement(
                                    "span"
                                );


                            revision.textContent =
                                (
                                    "RÉVISION "
                                    +
                                    setting.revision
                                );


                            const source =
                                document.createElement(
                                    "span"
                                );


                            source.textContent =
                                setting.source;


                            meta.append(
                                revision,
                                source
                            );


                            info.append(
                                title,
                                description,
                                meta
                            );


                            const control =
                                document.createElement(
                                    "div"
                                );


                            control.className =
                                "settings-control";


                            control.appendChild(
                                createControl(
                                    setting
                                )
                            );


                            card.append(
                                info,
                                control
                            );


                            container.appendChild(
                                card
                            );


                            if (
                                setting.can_update
                            ) {

                                editable =
                                    true;

                            }

                        }
                    );


                    const saveButton =
                        document.querySelector(
                            (
                                '[data-save-category="'
                                +
                                category
                                +
                                '"]'
                            )
                        );


                    if (saveButton) {

                        saveButton.hidden =
                            !editable;

                    }

                }
            );

        }


        function getControlValue(
            setting
        ) {

            if (
                setting.key
                ===
                "reports.default_sections"
            ) {

                return Array.from(
                    document.querySelectorAll(
                        (
                            'input[data-setting-key="'
                            +
                            setting.key
                            +
                            '"]:checked'
                        )
                    )
                ).map(
                    item =>
                        item.value
                );

            }


            const control =
                document.querySelector(
                    (
                        '[data-setting-key="'
                        +
                        setting.key
                        +
                        '"]'
                    )
                );


            if (!control) {

                return setting.value;

            }


            if (
                setting.data_type
                ===
                "boolean"
            ) {

                return Boolean(
                    control.checked
                );

            }


            return control.value;

        }


        async function saveCategory(
            category
        ) {

            const settings =
                state.settings.filter(
                    item =>
                        item.category
                        ===
                        category
                        &&
                        item.can_update
                );


            if (!settings.length) {

                return;

            }


            const button =
                document.querySelector(
                    (
                        '[data-save-category="'
                        +
                        category
                        +
                        '"]'
                    )
                );


            if (button) {

                button.disabled =
                    true;

            }


            try {

                for (
                    const setting
                    of settings
                ) {

                    const value =
                        getControlValue(
                            setting
                        );


                    await requestJson(
                        (
                            "/api/settings/"
                            +
                            encodeURIComponent(
                                setting.key
                            )
                        ),
                        {
                            method:
                                "PUT",

                            headers: {
                                "Content-Type":
                                    "application/json",
                            },

                            body:
                                JSON.stringify(
                                    {
                                        value:
                                            value
                                    }
                                ),
                        }
                    );

                }


                await loadSettings();


                showMessage(
                    "Paramètres enregistrés avec succès.",
                    "success"
                );

            }
            catch (error) {

                showMessage(
                    (
                        "Modification refusée : "
                        +
                        error.message
                    ),
                    "error"
                );

            }
            finally {

                if (button) {

                    button.disabled =
                        false;

                }

            }

        }


        document
            .querySelectorAll(
                "[data-save-category]"
            )
            .forEach(
                button => {

                    button.addEventListener(
                        "click",
                        () => {

                            saveCategory(
                                button.dataset.saveCategory
                            );

                        }
                    );

                }
            );


        function renderSummary() {

            const stats =
                state.settingsStats
                ||
                {};


            byId(
                "settings-kpi-total"
            ).textContent =
                stats.total
                ??
                "—";


            byId(
                "settings-kpi-readonly"
            ).textContent =
                stats.read_only
                ??
                "—";


            const editableCount =
                state.settings.filter(
                    setting =>
                        setting.can_update
                ).length;


            byId(
                "settings-kpi-mutable"
            ).textContent =
                editableCount;


            const integrity =
                (
                    state.audit
                    &&
                    state.audit.integrity
                );


            byId(
                "settings-kpi-audit"
            ).textContent =
                (
                    integrity
                    ?
                    (
                        integrity.valid
                        ?
                        "OK"
                        :
                        "ALERTE"
                    )
                    :
                    "PROTÉGÉ"
                );


            byId(
                "settings-kpi-audit-caption"
            ).textContent =
                (
                    integrity
                    ?
                    (
                        integrity.valid
                        ?
                        "Chaîne d'audit valide"
                        :
                        "Vérification requise"
                    )
                    :
                    "Accès selon autorisation"
                );


            const product =
                (
                    state.installation
                    &&
                    state.installation.product
                )
                ||
                {};


            const site =
                (
                    state.installation
                    &&
                    state.installation.site
                )
                ||
                {};


            const interfaceData =
                (
                    state.installation
                    &&
                    state.installation.interface
                )
                ||
                {};


            byId(
                "settings-overview-version"
            ).textContent =
                product.version
                ||
                "—";


            byId(
                "settings-overview-language"
            ).textContent =
                (
                    interfaceData.default_language
                    ===
                    "fr"
                    ?
                    "FRANÇAIS"
                    :
                    (
                        interfaceData.default_language
                        ||
                        "—"
                    ).toUpperCase()
                );


            byId(
                "settings-overview-role"
            ).textContent =
                (
                    state.permissions
                    &&
                    state.permissions.role
                )
                ||
                "—";


            byId(
                "settings-overview-site"
            ).textContent =
                site.name
                ||
                "NON CONFIGURÉ";


            byId(
                "settings-last-update-version"
            ).textContent =
                (
                    "Version "
                    +
                    (
                        product.version
                        ||
                        "—"
                    )
                );


            byId(
                "settings-about-version"
            ).textContent =
                (
                    "Version "
                    +
                    (
                        product.version
                        ||
                        "—"
                    )
                    +
                    " · "
                    +
                    (
                        product.codename
                        ||
                        "Enterprise"
                    )
                );


            byId(
                "settings-license-name"
            ).textContent =
                product.license
                ||
                "—";

        }


        function renderPermissions() {

            if (!state.permissions) {

                return;

            }


            byId(
                "settings-security-user"
            ).textContent =
                state.permissions.username
                ||
                "—";


            byId(
                "settings-security-role"
            ).textContent =
                state.permissions.role
                ||
                "—";


            const groups =
                state.permissions
                    .permission_status_groups
                ||
                [];


            let allowedCount = 0;

            let restrictedCount = 0;


            groups.forEach(
                group => {

                    group.permissions.forEach(
                        permission => {

                            if (
                                permission.allowed
                            ) {

                                allowedCount += 1;

                            }
                            else {

                                restrictedCount += 1;

                            }

                        }
                    );

                }
            );


            byId(
                "settings-permissions-allowed"
            ).textContent =
                allowedCount;


            byId(
                "settings-permissions-restricted"
            ).textContent =
                restrictedCount;


            const container =
                byId(
                    "settings-my-permissions"
                );


            container.innerHTML =
                "";


            groups.forEach(
                group => {

                    const card =
                        document.createElement(
                            "section"
                        );


                    card.className =
                        "settings-permission-group";


                    const heading =
                        document.createElement(
                            "div"
                        );


                    heading.className =
                        "settings-permission-group-heading";


                    const title =
                        document.createElement(
                            "strong"
                        );


                    title.textContent =
                        group.label;


                    const groupAllowed =
                        group.permissions.filter(
                            permission =>
                                permission.allowed
                        ).length;


                    const groupCount =
                        document.createElement(
                            "span"
                        );


                    groupCount.textContent =
                        (
                            groupAllowed
                            +
                            " / "
                            +
                            group.permissions.length
                        );


                    heading.append(
                        title,
                        groupCount
                    );


                    const rows =
                        document.createElement(
                            "div"
                        );


                    rows.className =
                        "settings-permission-rows";


                    group.permissions.forEach(
                        permission => {

                            const row =
                                document.createElement(
                                    "div"
                                );


                            row.className =
                                (
                                    "settings-permission-row "
                                    +
                                    (
                                        permission.allowed
                                        ?
                                        "allowed"
                                        :
                                        "restricted"
                                    )
                                );


                            const label =
                                document.createElement(
                                    "span"
                                );


                            label.textContent =
                                permission.label;


                            const status =
                                document.createElement(
                                    "strong"
                                );


                            status.className =
                                (
                                    "settings-permission-state "
                                    +
                                    (
                                        permission.allowed
                                        ?
                                        "allowed"
                                        :
                                        "restricted"
                                    )
                                );


                            status.textContent =
                                permission.allowed
                                ?
                                "AUTORISÉ"
                                :
                                "RESTREINT";


                            row.append(
                                label,
                                status
                            );


                            rows.appendChild(
                                row
                            );

                        }
                    );


                    card.append(
                        heading,
                        rows
                    );


                    container.appendChild(
                        card
                    );

                }
            );


            const rulesContainer =
                byId(
                    "settings-mandatory-rules"
                );


            if (rulesContainer) {

                rulesContainer.innerHTML =
                    "";


                const rules =
                    state.permissions
                        .mandatory_security_rules
                    ||
                    [];


                rules.forEach(
                    rule => {

                        const card =
                            document.createElement(
                                "div"
                            );


                        card.className =
                            "settings-mandatory-rule";


                        const content =
                            document.createElement(
                                "div"
                            );


                        const title =
                            document.createElement(
                                "strong"
                            );


                        title.textContent =
                            rule.label;


                        const description =
                            document.createElement(
                                "p"
                            );


                        description.textContent =
                            rule.description;


                        content.append(
                            title,
                            description
                        );


                        const status =
                            document.createElement(
                                "span"
                            );


                        status.className =
                            "settings-rule-status";


                        status.textContent =
                            "OBLIGATOIRE";


                        card.append(
                            content,
                            status
                        );


                        rulesContainer.appendChild(
                            card
                        );

                    }
                );

            }

        }


        function renderMatrix() {

            const card =
                byId(
                    "settings-permission-matrix-card"
                );


            if (
                !state.matrix
                ||
                !card
            ) {

                return;

            }


            card.hidden =
                false;


            const body =
                byId(
                    "settings-permission-matrix"
                );


            body.innerHTML =
                "";


            const visiblePermissions =
                state.matrix.permissions.filter(
                    permission =>
                        (
                            permission.startsWith(
                                "settings."
                            )
                            ||
                            permission.startsWith(
                                "reports."
                            )
                            ||
                            permission.startsWith(
                                "anpr."
                            )
                            ||
                            permission.startsWith(
                                "history."
                            )
                            ||
                            permission.startsWith(
                                "watchlist."
                            )
                        )
                );


            visiblePermissions.forEach(
                permission => {

                    const row =
                        document.createElement(
                            "tr"
                        );


                    const label =
                        document.createElement(
                            "td"
                        );


                    label.textContent =
                        (
                            state.matrix
                            .permission_labels[
                                permission
                            ]
                            ||
                            permissionLabel(
                                permission
                            )
                        );


                    row.appendChild(
                        label
                    );


                    state.matrix.roles.forEach(
                        role => {

                            const cell =
                                document.createElement(
                                    "td"
                                );


                            const allowed =
                                Boolean(
                                    state.matrix.matrix[
                                        role
                                    ][
                                        permission
                                    ]
                                );


                            cell.textContent =
                                allowed
                                ?
                                "✓"
                                :
                                "—";


                            cell.className =
                                allowed
                                ?
                                "yes"
                                :
                                "no";


                            row.appendChild(
                                cell
                            );

                        }
                    );


                    body.appendChild(
                        row
                    );

                }
            );

        }


        function renderAudit() {

            if (!state.audit) {

                return;

            }


            const navigation =
                byId(
                    "settings-audit-navigation"
                );


            if (navigation) {

                navigation.hidden =
                    false;

            }


            const integrity =
                state.audit.integrity
                ||
                {};


            byId(
                "settings-audit-integrity"
            ).textContent =
                integrity.valid
                ?
                (
                    "INTÉGRITÉ VALIDÉE · "
                    +
                    integrity.events
                    +
                    " ÉVÉNEMENT(S)"
                )
                :
                "ANOMALIE D'INTÉGRITÉ";


            const table =
                byId(
                    "settings-audit-table"
                );


            table.innerHTML =
                "";


            state.audit.events.forEach(
                event => {

                    const row =
                        document.createElement(
                            "tr"
                        );


                    const values = [

                        event.action,

                        labels[
                            event.setting_key
                        ]
                        ||
                        event.setting_key,

                        event.actor,

                        event.actor_role,

                        new Date(
                            event.timestamp
                        ).toLocaleString(
                            "fr-FR"
                        ),

                    ];


                    values.forEach(
                        value => {

                            const cell =
                                document.createElement(
                                    "td"
                                );


                            cell.textContent =
                                value
                                ??
                                "—";


                            row.appendChild(
                                cell
                            );

                        }
                    );


                    table.appendChild(
                        row
                    );

                }
            );

        }


        function renderInstallation() {

            if (!state.installation) {

                return;

            }


            const container =
                byId(
                    "settings-installation-grid"
                );


            container.innerHTML =
                "";


            const product =
                state.installation.product
                ||
                {};


            const installation =
                state.installation.installation
                ||
                {};


            const site =
                state.installation.site
                ||
                {};


            const runtime =
                state.installation.runtime
                ||
                {};



            const installationType = (
                installation.type
                ===
                "LOCAL"
                ?
                "Locale"
                :
                (
                    installation.type
                    ||
                    "—"
                )
            );


            const managementType = (
                installation.management
                ===
                "LOCAL"
                ?
                "Locale"
                :
                (
                    installation.management
                    ||
                    "—"
                )
            );


            const updateManagement = (
                installation.update_management
                ===
                "PHOENIX_CONTROL_CENTER_FUTURE"
                ?
                "Phoenix Control Center · prévu"
                :
                (
                    installation.update_management
                    ||
                    "—"
                )
            );


            const aboutProduct =
                byId(
                    "settings-about-product"
                );

            if (aboutProduct) {

                aboutProduct.textContent =
                    product.name
                    ||
                    "—";

            }


            const aboutVersion =
                byId(
                    "settings-about-version"
                );

            if (aboutVersion) {

                const versionParts = [];


                if (product.version) {

                    versionParts.push(
                        "Version "
                        +
                        product.version
                    );

                }


                if (product.codename) {

                    versionParts.push(
                        "Édition "
                        +
                        product.codename
                    );

                }


                aboutVersion.textContent = (
                    versionParts.join(
                        " · "
                    )
                    ||
                    "Version —"
                );

            }


            const legalPublisher =
                byId(
                    "settings-legal-publisher-kicker"
                );

            if (legalPublisher) {

                legalPublisher.textContent = (
                    product.publisher
                    ||
                    "ÉDITEUR"
                ).toUpperCase();

            }


            const copyright =
                byId(
                    "settings-about-copyright"
                );

            if (copyright) {

                copyright.textContent = (
                    "© "
                    +
                    new Date().getFullYear()
                    +
                    " "
                    +
                    (
                        product.publisher
                        ||
                        "Phoenix Security Technologies"
                    )
                    +
                    ". Tous droits réservés."
                );

            }


            const licenseName =
                byId(
                    "settings-license-name"
                );

            if (licenseName) {

                licenseName.textContent =
                    product.license
                    ||
                    "—";

            }


            const licenseDescription =
                byId(
                    "settings-license-description"
                );

            if (licenseDescription) {

                licenseDescription.textContent = (
                    (
                        product.name
                        ||
                        "Ce produit"
                    )
                    +
                    " est un logiciel propriétaire. "
                    +
                    "Les composants tiers restent soumis "
                    +
                    "à leurs licences respectives."
                );

            }

            const values = [

                [
                    "PRODUIT",
                    product.name
                ],

                [
                    "VERSION",
                    product.version
                ],

                [
                    "ÉDITION",
                    product.codename
                ],

                [
                    "ÉDITEUR",
                    product.publisher
                ],

                [
                    "LICENCE",
                    product.license
                    ||
                    "—"
                ],

                [
                    "INSTALLATION",
                    installationType
                ],

                [
                    "GESTION",
                    managementType
                ],

                [
                    "MISES À JOUR",
                    updateManagement
                ],

                [
                    "SITE",
                    site.name
                    ||
                    "Non configuré"
                ],

                [
                    "VILLE / PAYS",
                    (
                        (
                            site.city
                            ||
                            "Non configurée"
                        )
                        +
                        " · "
                        +
                        (
                            site.country_code
                            ||
                            "—"
                        )
                    )
                ],

                [
                    "FUSEAU HORAIRE",
                    site.timezone
                ],

                [
                    "SYSTÈME",
                    (
                        runtime.operating_system
                        +
                        " "
                        +
                        runtime.os_release
                    )
                ],

                [
                    "ARCHITECTURE",
                    runtime.architecture
                ],

                [
                    "PYTHON",
                    runtime.python_version
                ],

            ];


            values.forEach(
                (
                    [
                        label,
                        value
                    ]
                ) => {

                    const card =
                        document.createElement(
                            "article"
                        );


                    card.className =
                        (
                            "phx-panel "
                            +
                            "settings-installation-card"
                        );


                    const labelElement =
                        document.createElement(
                            "span"
                        );


                    labelElement.textContent =
                        label;


                    const valueElement =
                        document.createElement(
                            "strong"
                        );


                    valueElement.textContent =
                        value
                        ||
                        "—";


                    card.append(
                        labelElement,
                        valueElement
                    );


                    container.appendChild(
                        card
                    );

                }
            );

        }


        async function loadSettings() {

            const response =
                await requestJson(
                    "/api/settings"
                );


            state.settings =
                response.settings
                ||
                [];


            state.settingsStats =
                response.stats
                ||
                {};


            renderCategories();

        }


        async function loadAll() {

            try {

                const [
                    capabilities,
                    installation,
                    permissions,
                    languages
                ] = await Promise.all(
                    [
                        requestJson(
                            "/api/settings/capabilities"
                        ),

                        requestJson(
                            "/api/settings/installation"
                        ),

                        requestJson(
                            "/api/settings/permissions/me"
                        ),

                        optionalRequestJson(
                            "/api/settings/languages"
                        ),
                    ]
                );


                state.capabilities =
                    capabilities.capabilities
                    ||
                    {};


                state.installation =
                    installation;


                state.permissions =
                    permissions;


                state.languages =
                    languages;


                await loadSettings();


                if (
                    state.capabilities
                        .view_permission_matrix
                ) {

                    try {

                        state.matrix =
                            await optionalRequestJson(
                                (
                                    "/api/settings/"
                                    +
                                    "permissions/matrix"
                                )
                            );

                    }
                    catch {

                        state.matrix =
                            null;

                    }

                }


                if (
                    state.capabilities
                        .view_audit
                ) {

                    try {

                        state.audit =
                            await optionalRequestJson(
                                "/api/settings/audit"
                            );

                    }
                    catch {

                        state.audit =
                            null;

                    }

                }


                renderSummary();

                renderPermissions();

                renderMatrix();

                renderAudit();

                renderInstallation();

            }
            catch (error) {

                if (
                    error.status
                    ===
                    401
                ) {

                    window.location.href =
                        "/login";

                    return;

                }


                showMessage(
                    (
                        "Impossible de charger "
                        +
                        "les paramètres : "
                        +
                        error.message
                    ),
                    "error"
                );

            }

        }


        loadAll();

    }
);
