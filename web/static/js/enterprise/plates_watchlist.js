/*
========================================================
PHOENIX VISION AI
Plaques / LAPI — Gouvernance Watchlist
v4.7.6
========================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    () => {


        const modal =
            document.getElementById(
                "watchlist-modal"
            );


        const openButton =
            document.getElementById(
                "plates-watchlist-button"
            );


        const closeButton =
            document.getElementById(
                "watchlist-close"
            );


        const backdrop =
            document.getElementById(
                "watchlist-modal-backdrop"
            );


        const form =
            document.getElementById(
                "watchlist-form"
            );


        const submitButton =
            document.getElementById(
                "watchlist-submit"
            );


        const formMessage =
            document.getElementById(
                "watchlist-form-message"
            );


        const pendingList =
            document.getElementById(
                "watchlist-pending-list"
            );


        const pendingCount =
            document.getElementById(
                "watchlist-pending-count"
            );


        const auditPanel =
            document.getElementById(
                "watchlist-audit-panel"
            );


        const auditList =
            document.getElementById(
                "watchlist-audit-list"
            );


        const proposalState =
            document.getElementById(
                "watchlist-proposal-state"
            );


        if(
            !modal
            ||
            !openButton
            ||
            !form
        ) {

            return;

        }


        let capabilities = {

            match: false,
            view: false,
            propose: false,
            approve_local: false

        };


        function text(
            value,
            fallback="—"
        ) {

            if(
                value === null
                ||
                value === undefined
                ||
                String(value).trim() === ""
            ) {

                return fallback;

            }


            return String(
                value
            );

        }


        function escapeHtml(
            value
        ) {

            return text(
                value,
                ""
            )
            .replaceAll(
                "&",
                "&amp;"
            )
            .replaceAll(
                "<",
                "&lt;"
            )
            .replaceAll(
                ">",
                "&gt;"
            )
            .replaceAll(
                '"',
                "&quot;"
            )
            .replaceAll(
                "'",
                "&#039;"
            );

        }


        function formatDate(
            value
        ) {

            if(!value) {
                return "—";
            }


            const date =
                new Date(
                    value
                );


            if(
                Number.isNaN(
                    date.getTime()
                )
            ) {

                return text(
                    value
                );

            }


            return date.toLocaleString(
                "fr-FR"
            );

        }


        function currentPlate() {

            const search =
                document.getElementById(
                    "plates-search-input"
                );


            const searchValue =
                search
                ?
                search.value.trim()
                :
                "";


            /*
            Une plaque saisie manuellement
            est prioritaire.
            */

            if(searchValue) {

                return searchValue;

            }


            const detail =
                document.getElementById(
                    "plates-detail-plate"
                );


            const detailValue =
                detail
                ?
                detail.textContent.trim()
                :
                "";


            if(
                detailValue
                &&
                detailValue !== "—"
            ) {

                return detailValue;

            }


            return "";

        }


        function normalizedCurrentPlate() {

            return currentPlate()
                .toUpperCase()
                .replace(
                    /[^A-Z0-9]/g,
                    ""
                );

        }


        function syncWatchlistButton() {

            const allowed =
                capabilities.propose
                ===
                true;


            /*
            Le bouton n'existe dans l'interface
            que pour un utilisateur habilité.
            */

            openButton.hidden =
                !allowed;


            if(!allowed) {

                openButton.disabled =
                    true;

                openButton.setAttribute(
                    "aria-disabled",
                    "true"
                );

                return;

            }


            const plate =
                normalizedCurrentPlate();


            const usable =
                plate.length >= 3;


            openButton.disabled =
                !usable;


            openButton.setAttribute(
                "aria-disabled",
                String(
                    !usable
                )
            );


            openButton.title =
                usable
                ?
                "Proposer cette plaque à la surveillance"
                :
                "Saisissez ou sélectionnez d'abord une plaque";

        }



        function showMessage(
            message,
            type=""
        ) {

            formMessage.hidden =
                false;


            formMessage.className =
                "watchlist-form-message"
                +
                (
                    type
                    ?
                    " " + type
                    :
                    ""
                );


            formMessage.textContent =
                message;

        }


        function clearMessage() {

            formMessage.hidden =
                true;

            formMessage.textContent =
                "";

        }


        function openModal() {

            if(
                !capabilities.propose
                &&
                !capabilities.view
            ) {

                return;

            }


            const plate =
                normalizedCurrentPlate();


            /*
            Une proposition de surveillance
            ne peut pas être ouverte sans plaque.
            */

            if(
                plate.length < 3
            ) {

                syncWatchlistButton();

                return;

            }


            const plateInput =
                document.getElementById(
                    "watchlist-plate"
                );


            if(plateInput) {

                plateInput.value =
                    plate;

            }


            clearMessage();


            modal.removeAttribute(
                "hidden"
            );


            modal.hidden =
                false;


            modal.style.setProperty(
                "display",
                "flex",
                "important"
            );


            document.body.style.overflow =
                "hidden";


            if(
                capabilities.view
            ) {

                loadPending();

            }

        }


        /*
        Fonction publique volontairement très petite.

        Elle permet au bouton HTML de demander
        directement l'ouverture du centre de
        gouvernance, même si son élément DOM
        a été reconstruit par l'interface.
        */

        window.phoenixOpenWatchlist =
            function(
                event
            ) {

                if(event) {

                    event.preventDefault();

                    event.stopPropagation();

                }


                openModal();

            };



        function closeModal() {

            modal.hidden =
                true;

            modal.setAttribute(
                "hidden",
                ""
            );

            modal.style.display =
                "";


            document.body.style.overflow =
                "";

        }


        async function loadCapabilities() {

            try {

                const response =
                    await fetch(
                        "/api/watchlist/capabilities/me",
                        {
                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
                        }
                    );


                if(
                    response.status
                    ===
                    401
                ) {

                    return;

                }


                if(!response.ok) {

                    return;

                }


                const data =
                    await response.json();


                capabilities =
                    data.capabilities
                    ||
                    capabilities;


                syncWatchlistButton();


                document.getElementById(
                    "watchlist-review-panel"
                ).hidden =
                    !capabilities.view;


                form.hidden =
                    !capabilities.propose;


                if(
                    !capabilities.propose
                ) {

                    proposalState.textContent =
                        "LECTURE SEULE";


                    proposalState.className =
                        "phx-status neutral";

                }

            }
            catch(error) {

                console.error(
                    "Phoenix Watchlist capabilities:",
                    error
                );

            }

        }


        function renderPending(
            records
        ) {

            const pending =
                records.filter(
                    record =>

                        String(
                            record.status
                            ||
                            ""
                        ).toUpperCase()
                        ===
                        "PENDING"
                );


            pendingCount.textContent =
                pending.length
                +
                (
                    pending.length > 1
                    ?
                    " dossiers"
                    :
                    " dossier"
                );


            if(
                pending.length === 0
            ) {

                pendingList.innerHTML = `

                    <div class="watchlist-empty-state">

                        <strong>
                            AUCUNE PROPOSITION EN ATTENTE
                        </strong>

                        <span>
                            Les nouvelles propositions
                            apparaîtront ici.
                        </span>

                    </div>
                `;


                auditPanel.hidden =
                    true;


                return;

            }


            pendingList.innerHTML =
                "";


            pending.forEach(
                record => {


                    const card =
                        document.createElement(
                            "article"
                        );


                    card.className =
                        "watchlist-card";


                    const approveButton =
                        capabilities.approve_local
                        ?
                        `
                        <button
                            type="button"
                            class="phx-button"
                            data-action="approve"
                        >
                            APPROUVER
                        </button>
                        `
                        :
                        "";


                    card.innerHTML = `

                        <div class="watchlist-card-top">

                            <div>

                                <div class="watchlist-card-plate">
                                    ${escapeHtml(
                                        record.plate
                                    )}
                                </div>

                                <span class="watchlist-card-category">
                                    ${escapeHtml(
                                        record.category_label
                                    )}
                                </span>

                            </div>

                            <span class="phx-status warning">
                                EN ATTENTE
                            </span>

                        </div>


                        <div class="watchlist-card-meta">

                            <div>

                                <span>
                                    Priorité
                                </span>

                                <strong>
                                    ${escapeHtml(
                                        record.priority_label
                                    )}
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Créé par
                                </span>

                                <strong>
                                    ${escapeHtml(
                                        record.created_by
                                    )}
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Référence
                                </span>

                                <strong>
                                    ${escapeHtml(
                                        record.case_reference
                                    )}
                                </strong>

                            </div>


                            <div>

                                <span>
                                    Création
                                </span>

                                <strong>
                                    ${escapeHtml(
                                        formatDate(
                                            record.created_at
                                        )
                                    )}
                                </strong>

                            </div>

                        </div>


                        <div class="watchlist-card-actions">

                            <button
                                type="button"
                                class="phx-button"
                                data-action="audit"
                            >
                                JOURNAL
                            </button>

                            ${approveButton}

                        </div>
                    `;


                    const auditButton =
                        card.querySelector(
                            '[data-action="audit"]'
                        );


                    auditButton.addEventListener(
                        "click",
                        () => {

                            loadAudit(
                                record.uuid
                            );

                        }
                    );


                    const approve =
                        card.querySelector(
                            '[data-action="approve"]'
                        );


                    if(approve) {

                        approve.addEventListener(
                            "click",
                            () => {

                                approveEntry(
                                    record.uuid,
                                    approve
                                );

                            }
                        );

                    }


                    pendingList.appendChild(
                        card
                    );

                }
            );

        }


        async function loadPending() {

            if(
                !capabilities.view
            ) {

                return;

            }


            try {

                const response =
                    await fetch(
                        "/api/watchlist?limit=250",
                        {
                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
                        }
                    );


                if(!response.ok) {

                    return;

                }


                const data =
                    await response.json();


                renderPending(
                    Array.isArray(
                        data.records
                    )
                    ?
                    data.records
                    :
                    []
                );

            }
            catch(error) {

                console.error(
                    "Phoenix Watchlist list:",
                    error
                );

            }

        }


        async function loadAudit(
            entryUuid
        ) {

            if(
                !capabilities.view
            ) {

                return;

            }


            const response =
                await fetch(
                    "/api/watchlist/"
                    +
                    encodeURIComponent(
                        entryUuid
                    )
                    +
                    "/audit",
                    {
                        credentials:
                            "same-origin",

                        cache:
                            "no-store"
                    }
                );


            if(!response.ok) {

                return;

            }


            const data =
                await response.json();


            const events =
                Array.isArray(
                    data.events
                )
                ?
                data.events
                :
                [];


            auditList.innerHTML =
                "";


            events.forEach(
                event => {


                    const item =
                        document.createElement(
                            "div"
                        );


                    item.className =
                        "watchlist-audit-event";


                    item.innerHTML = `

                        <strong>
                            ${escapeHtml(
                                event.action
                            )}
                        </strong>

                        <span>
                            ${escapeHtml(
                                event.actor
                            )}
                            ·
                            ${escapeHtml(
                                formatDate(
                                    event.timestamp
                                )
                            )}
                        </span>

                        <span>
                            ${escapeHtml(
                                event.details
                            )}
                        </span>
                    `;


                    auditList.appendChild(
                        item
                    );

                }
            );


            auditPanel.hidden =
                false;

        }


        async function approveEntry(
            entryUuid,
            button
        ) {

            if(
                !capabilities.approve_local
            ) {

                return;

            }


            button.disabled =
                true;


            try {

                const response =
                    await fetch(
                        "/api/watchlist/"
                        +
                        encodeURIComponent(
                            entryUuid
                        )
                        +
                        "/approve",
                        {
                            method:
                                "POST",

                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
                        }
                    );


                const data =
                    await response.json();


                if(!response.ok) {

                    console.error(
                        "Phoenix approval:",
                        data
                    );

                    return;

                }


                await loadPending();

            }
            finally {

                button.disabled =
                    false;

            }

        }


        form.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                if(
                    !capabilities.propose
                ) {

                    return;

                }


                clearMessage();


                const payload = {

                    plate:
                        document.getElementById(
                            "watchlist-plate"
                        ).value.trim(),

                    category:
                        document.getElementById(
                            "watchlist-category"
                        ).value,

                    priority:
                        document.getElementById(
                            "watchlist-priority"
                        ).value,

                    reason:
                        document.getElementById(
                            "watchlist-reason"
                        ).value.trim(),

                    case_reference:
                        document.getElementById(
                            "watchlist-case-reference"
                        ).value.trim(),

                    authority:
                        document.getElementById(
                            "watchlist-authority"
                        ).value.trim(),

                    valid_until:
                        document.getElementById(
                            "watchlist-valid-until"
                        ).value
                        ||
                        null

                };


                submitButton.disabled =
                    true;


                proposalState.textContent =
                    "ENVOI";


                proposalState.className =
                    "phx-status warning";


                try {

                    const response =
                        await fetch(
                            "/api/watchlist/propose",
                            {
                                method:
                                    "POST",

                                credentials:
                                    "same-origin",

                                cache:
                                    "no-store",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    )
                            }
                        );


                    const data =
                        await response.json();


                    if(!response.ok) {

                        showMessage(
                            (
                                "La proposition n'a pas été enregistrée. "
                                +
                                text(
                                    data.error,
                                    "Vérifiez les informations."
                                )
                            ),
                            "error"
                        );


                        proposalState.textContent =
                            "ERREUR";


                        proposalState.className =
                            "phx-status warning";


                        return;

                    }


                    showMessage(
                        (
                            "Proposition enregistrée. "
                            +
                            "Elle est maintenant en attente "
                            +
                            "d'une validation autorisée."
                        ),
                        "success"
                    );


                    proposalState.textContent =
                        "EN ATTENTE";


                    proposalState.className =
                        "phx-status warning";


                    document.getElementById(
                        "watchlist-reason"
                    ).value =
                        "";


                    document.getElementById(
                        "watchlist-case-reference"
                    ).value =
                        "";


                    document.getElementById(
                        "watchlist-authority"
                    ).value =
                        "";


                    document.getElementById(
                        "watchlist-valid-until"
                    ).value =
                        "";


                    if(
                        capabilities.view
                    ) {

                        await loadPending();

                    }

                }
                catch(error) {

                    console.error(
                        "Phoenix Watchlist propose:",
                        error
                    );


                    showMessage(
                        "Erreur de communication avec Phoenix.",
                        "error"
                    );


                    proposalState.textContent =
                        "ERREUR";


                    proposalState.className =
                        "phx-status warning";

                }
                finally {

                    submitButton.disabled =
                        false;

                }

            }
        );


        /*
        ====================================================
        OUVERTURE WATCHLIST

        Délégation en phase capture :
        robuste même si l'interface reconstruit le bouton.
        ====================================================
        */

        document.addEventListener(
            "click",
            event => {

                const target =
                    event.target;


                if(
                    !(target instanceof Element)
                ) {

                    return;

                }


                const trigger =
                    target.closest(
                        "#plates-watchlist-button"
                    );


                if(!trigger) {

                    return;

                }


                event.preventDefault();


                openModal();

            },
            true
        );



        closeButton.addEventListener(
            "click",
            closeModal
        );


        backdrop.addEventListener(
            "click",
            closeModal
        );


        document.addEventListener(
            "keydown",
            event => {

                if(
                    event.key === "Escape"
                    &&
                    !modal.hidden
                ) {

                    closeModal();

                }

            }
        );


        const plateSearchInput =
            document.getElementById(
                "plates-search-input"
            );


        if(plateSearchInput) {

            plateSearchInput.addEventListener(
                "input",
                syncWatchlistButton
            );

        }


        const plateList =
            document.getElementById(
                "plates-list"
            );


        if(plateList) {

            plateList.addEventListener(
                "click",
                () => {

                    window.setTimeout(
                        syncWatchlistButton,
                        0
                    );

                }
            );

        }


        const resetSearchButton =
            document.getElementById(
                "plates-search-reset"
            );


        if(resetSearchButton) {

            resetSearchButton.addEventListener(
                "click",
                () => {

                    window.setTimeout(
                        () => {

                            openButton.disabled =
                                true;

                            openButton.setAttribute(
                                "aria-disabled",
                                "true"
                            );

                        },
                        0
                    );

                }
            );

        }


        loadCapabilities();


    }
);
