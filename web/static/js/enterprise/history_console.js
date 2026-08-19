/*
========================================================
PHOENIX VISION AI
Enterprise Vehicle History Console
Detailed Forensic Record v4.5.1
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const list =
            document.getElementById(
                "history-list"
            );

        const empty =
            document.getElementById(
                "history-empty"
            );

        const message =
            document.getElementById(
                "history-message"
            );

        const search =
            document.getElementById(
                "history-search"
            );

        const threatFilter =
            document.getElementById(
                "history-threat-filter"
            );

        const plateFilter =
            document.getElementById(
                "history-plate-filter"
            );

        const refreshTime =
            document.getElementById(
                "history-refresh-time"
            );


        let records = [];


        function escapeHtml(value) {

            const div =
                document.createElement(
                    "div"
                );

            div.textContent =
                String(value ?? "");

            return div.innerHTML;
        }


        function parsePhoenixDate(value) {

            if(!value) {
                return null;
            }


            let normalized =
                String(value)
                .trim();


            normalized =
                normalized.replace(
                    " ",
                    "T"
                );


            normalized =
                normalized.replace(
                    /(\.\d{3})\d+/,
                    "$1"
                );


            const date =
                new Date(
                    normalized
                );


            if(
                Number.isNaN(
                    date.getTime()
                )
            ) {
                return null;
            }


            return date;
        }


        function formatDate(value) {

            const date =
                parsePhoenixDate(
                    value
                );


            if(!date) {

                return value
                    ?
                    String(value)
                    :
                    "—";
            }


            return date.toLocaleString(
                "fr-FR",
                {
                    day: "2-digit",
                    month: "2-digit",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                }
            );
        }


        function formatDuration(
            firstSeen,
            lastSeen
        ) {

            const first =
                parsePhoenixDate(
                    firstSeen
                );

            const last =
                parsePhoenixDate(
                    lastSeen
                );


            if(
                !first
                ||
                !last
            ) {
                return "—";
            }


            let seconds =
                Math.max(
                    0,
                    Math.round(
                        (
                            last.getTime()
                            -
                            first.getTime()
                        )
                        /
                        1000
                    )
                );


            const hours =
                Math.floor(
                    seconds / 3600
                );

            seconds %= 3600;


            const minutes =
                Math.floor(
                    seconds / 60
                );

            seconds %= 60;


            const parts = [];


            if(hours) {
                parts.push(
                    `${hours} h`
                );
            }


            if(minutes) {
                parts.push(
                    `${minutes} min`
                );
            }


            parts.push(
                `${seconds} s`
            );


            return parts.join(" ");
        }


        function trajectoryGraphic(
            points
        ) {

            if(
                !Array.isArray(points)
                ||
                points.length < 2
            ) {

                return `

                    <div class="history-trajectory-empty">

                        Trajectoire insuffisante pour produire une trace.

                    </div>
                `;
            }


            const valid =
                points.filter(
                    point =>
                        Array.isArray(point)
                        &&
                        point.length >= 2
                        &&
                        Number.isFinite(
                            Number(point[0])
                        )
                        &&
                        Number.isFinite(
                            Number(point[1])
                        )
                );


            if(valid.length < 2) {

                return `

                    <div class="history-trajectory-empty">

                        Trajectoire insuffisante pour produire une trace.

                    </div>
                `;
            }


            const xs =
                valid.map(
                    point =>
                        Number(point[0])
                );


            const ys =
                valid.map(
                    point =>
                        Number(point[1])
                );


            const minX =
                Math.min(...xs);

            const maxX =
                Math.max(...xs);

            const minY =
                Math.min(...ys);

            const maxY =
                Math.max(...ys);


            const rangeX =
                Math.max(
                    1,
                    maxX - minX
                );


            const rangeY =
                Math.max(
                    1,
                    maxY - minY
                );


            const normalized =
                valid.map(
                    point => {

                        const x =
                            12
                            +
                            (
                                (
                                    Number(point[0])
                                    -
                                    minX
                                )
                                /
                                rangeX
                            )
                            *
                            276;


                        const y =
                            18
                            +
                            (
                                (
                                    Number(point[1])
                                    -
                                    minY
                                )
                                /
                                rangeY
                            )
                            *
                            104;


                        return [
                            x.toFixed(1),
                            y.toFixed(1)
                        ];

                    }
                );


            const polyline =
                normalized
                .map(
                    point =>
                        point.join(",")
                )
                .join(" ");


            const first =
                normalized[0];


            const last =
                normalized[
                    normalized.length - 1
                ];


            return `

                <div class="history-trajectory-visual">

                    <svg
                        viewBox="0 0 300 140"
                        role="img"
                        aria-label="Trajectoire relative du véhicule"
                    >

                        <defs>

                            <linearGradient
                                id="phoenixTrajectory"
                                x1="0"
                                y1="0"
                                x2="1"
                                y2="0"
                            >

                                <stop
                                    offset="0%"
                                    stop-color="#1da2ff"
                                />

                                <stop
                                    offset="100%"
                                    stop-color="#55c58a"
                                />

                            </linearGradient>

                        </defs>


                        <g class="trajectory-grid">

                            <line x1="0" y1="35" x2="300" y2="35"></line>
                            <line x1="0" y1="70" x2="300" y2="70"></line>
                            <line x1="0" y1="105" x2="300" y2="105"></line>

                            <line x1="75" y1="0" x2="75" y2="140"></line>
                            <line x1="150" y1="0" x2="150" y2="140"></line>
                            <line x1="225" y1="0" x2="225" y2="140"></line>

                        </g>


                        <polyline
                            class="trajectory-path"
                            points="${polyline}"
                        ></polyline>


                        <circle
                            class="trajectory-start"
                            cx="${first[0]}"
                            cy="${first[1]}"
                            r="4"
                        ></circle>


                        <circle
                            class="trajectory-end"
                            cx="${last[0]}"
                            cy="${last[1]}"
                            r="4"
                        ></circle>

                    </svg>


                    <div class="history-trajectory-legend">

                        <span>
                            ● Début
                        </span>

                        <span>
                            ${escapeHtml(valid.length)}
                            points persistés
                        </span>

                        <span>
                            ● Fin
                        </span>

                    </div>

                </div>
            `;
        }



        function displayValue(
            value,
            fallback="Non renseigné"
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


            return String(value);
        }


        function hasPlate(record) {

            return Boolean(
                String(
                    record.plate || ""
                ).trim()
            );
        }


        function safeThreatClass(value) {

            const threat =
                String(
                    value || "UNKNOWN"
                ).toUpperCase();


            if(
                [
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL"
                ].includes(
                    threat
                )
            ) {

                return threat;
            }


            return "UNKNOWN";
        }


        function createDetailShell() {

            if(
                document.getElementById(
                    "history-detail-overlay"
                )
            ) {
                return;
            }


            const overlay =
                document.createElement(
                    "div"
                );


            overlay.id =
                "history-detail-overlay";


            overlay.className =
                "history-detail-overlay";


            overlay.innerHTML = `

                <aside
                    class="history-detail-drawer"
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="history-detail-title"
                >

                    <header class="history-detail-header">

                        <div>

                            <div class="history-detail-kicker">
                                PHOENIX FORENSIC RECORD
                            </div>

                            <h2 id="history-detail-title">
                                Fiche historique
                            </h2>

                        </div>


                        <button
                            id="history-detail-close"
                            class="history-detail-close"
                            type="button"
                            aria-label="Fermer la fiche"
                        >
                            <span></span>
                            <span></span>
                        </button>

                    </header>


                    <div
                        id="history-detail-content"
                        class="history-detail-content"
                    >
                    </div>

                </aside>
            `;


            document.body.appendChild(
                overlay
            );


            const closeButton =
                document.getElementById(
                    "history-detail-close"
                );


            closeButton.addEventListener(
                "click",
                closeDetail
            );


            overlay.addEventListener(
                "click",
                event => {

                    if(
                        event.target
                        ===
                        overlay
                    ) {

                        closeDetail();
                    }

                }
            );


            document.addEventListener(
                "keydown",
                event => {

                    if(
                        event.key
                        ===
                        "Escape"
                    ) {

                        closeDetail();
                    }

                }
            );
        }


        function closeDetail() {

            const overlay =
                document.getElementById(
                    "history-detail-overlay"
                );


            if(!overlay) {
                return;
            }


            overlay.classList.remove(
                "open"
            );


            document.body.classList.remove(
                "history-detail-open"
            );
        }


        function detailField(
            label,
            value,
            extraClass=""
        ) {

            return `

                <div class="history-detail-field ${extraClass}">

                    <span>
                        ${escapeHtml(label)}
                    </span>

                    <strong>
                        ${escapeHtml(value)}
                    </strong>

                </div>
            `;
        }


        function renderDetail(
            record
        ) {

            const content =
                document.getElementById(
                    "history-detail-content"
                );


            const threat =
                safeThreatClass(
                    record.threat_level
                );


            const label =
                displayValue(
                    record.label,
                    "UNKNOWN"
                ).toUpperCase();


            const tracker =
                displayValue(
                    record.tracker_id,
                    "—"
                );


            const plate =
                displayValue(
                    record.plate,
                    "NON LUE"
                );


            const duration =
                formatDuration(
                    record.first_seen,
                    record.last_seen
                );


            const maxSpeed =
                Number(
                    record.max_speed || 0
                );


            content.innerHTML = `

                <section class="history-record-hero">

                    <div class="history-record-symbol">

                        <svg class="phoenix-icon">
                            <use href="/static/icons/phoenix-ui.svg#icon-history"></use>
                        </svg>

                    </div>


                    <div class="history-record-identity">

                        <div class="history-record-state">
                            ENREGISTREMENT PERSISTANT
                        </div>

                        <h3>
                            ${escapeHtml(label)}
                            <span>
                                TRACKER ${escapeHtml(tracker)}
                            </span>
                        </h3>

                        <div class="history-record-uuid">
                            ${escapeHtml(record.uuid || "—")}
                        </div>

                    </div>


                    <div class="history-record-plate">
                        <span>PLAQUE</span>
                        <strong>
                            ${escapeHtml(plate)}
                        </strong>
                    </div>

                </section>


                <section class="history-detail-metrics">

                    <article>

                        <span>OBSERVATION</span>

                        <strong>
                            ${escapeHtml(duration)}
                        </strong>

                    </article>


                    <article>

                        <span>FRAMES</span>

                        <strong>
                            ${escapeHtml(
                                displayValue(
                                    record.total_frames,
                                    "0"
                                )
                            )}
                        </strong>

                    </article>


                    <article>

                        <span>THREAT SCORE</span>

                        <strong class="threat-text ${escapeHtml(threat)}">
                            ${escapeHtml(
                                displayValue(
                                    record.threat_score,
                                    "0"
                                )
                            )}/100
                        </strong>

                    </article>


                    <article>

                        <span>NIVEAU</span>

                        <strong class="threat-text ${escapeHtml(threat)}">
                            ${escapeHtml(threat)}
                        </strong>

                    </article>

                </section>


                <section class="history-detail-section">

                    <div class="history-section-title">

                        <div>
                            IDENTIFICATION DU VÉHICULE
                        </div>

                        <span>
                            DONNÉES PERSISTANTES
                        </span>

                    </div>


                    <div class="history-detail-grid">

                        ${detailField(
                            "Type",
                            displayValue(
                                record.label
                            )
                        )}

                        ${detailField(
                            "Tracker ID",
                            tracker
                        )}

                        ${detailField(
                            "Plaque reconnue",
                            plate
                        )}

                        ${detailField(
                            "Couleur",
                            displayValue(
                                record.color
                            )
                        )}

                        ${detailField(
                            "Marque",
                            displayValue(
                                record.brand
                            )
                        )}

                        ${detailField(
                            "Modèle",
                            displayValue(
                                record.model
                            )
                        )}

                    </div>

                </section>


                <section class="history-detail-section">

                    <div class="history-section-title">

                        <div>
                            CHRONOLOGIE
                        </div>

                        <span>
                            SUIVI PHOENIX
                        </span>

                    </div>


                    <div class="history-timeline">

                        <div class="history-timeline-event">

                            <span class="history-timeline-dot"></span>

                            <div>

                                <span>
                                    PREMIÈRE DÉTECTION
                                </span>

                                <strong>
                                    ${escapeHtml(
                                        formatDate(
                                            record.first_seen
                                        )
                                    )}
                                </strong>

                            </div>

                        </div>


                        <div class="history-timeline-line"></div>


                        <div class="history-timeline-event">

                            <span class="history-timeline-dot end"></span>

                            <div>

                                <span>
                                    DERNIÈRE DÉTECTION
                                </span>

                                <strong>
                                    ${escapeHtml(
                                        formatDate(
                                            record.last_seen
                                        )
                                    )}
                                </strong>

                            </div>

                        </div>

                    </div>


                    <div class="history-detail-grid">

                        ${detailField(
                            "Durée observée",
                            duration
                        )}

                        ${detailField(
                            "Frames suivies",
                            displayValue(
                                record.total_frames,
                                "0"
                            )
                        )}

                        ${detailField(
                            "Direction",
                            displayValue(
                                record.direction
                            )
                        )}

                        ${detailField(
                            "Vitesse max relative",
                            `${maxSpeed} px/frame`
                        )}

                    </div>

                </section>


                <section class="history-detail-section">

                    <div class="history-section-title">

                        <div>
                            LOCALISATION & TRAJECTOIRE
                        </div>

                        <span>
                            CONTEXTE OPÉRATIONNEL
                        </span>

                    </div>


                    <div class="history-detail-grid">

                        ${detailField(
                            "Dernière zone connue",
                            displayValue(
                                record.zone,
                                "Aucune zone"
                            )
                        )}

                        ${detailField(
                            "Dernière caméra",
                            displayValue(
                                record.last_camera,
                                "Non renseignée"
                            )
                        )}

                        ${detailField(
                            "Caméras observées",
                            Array.isArray(
                                record.cameras_seen
                            )
                            &&
                            record.cameras_seen.length
                            ?
                            record.cameras_seen.join(
                                " → "
                            )
                            :
                            "Non renseignées"
                        )}

                        ${detailField(
                            "Zones traversées",
                            Array.isArray(
                                record.zones_history
                            )
                            &&
                            record.zones_history.length
                            ?
                            record.zones_history.join(
                                " → "
                            )
                            :
                            "Aucune zone"
                        )}

                    </div>


                    <div class="history-trajectory-block">

                        <div class="history-trajectory-title">

                            <div>
                                TRACE DE SUIVI CAMÉRA
                            </div>

                            <span>
                                TRAJECTOIRE RELATIVE
                                ·
                                PAS GPS
                            </span>

                        </div>


                        ${trajectoryGraphic(
                            record.trajectory
                        )}

                    </div>

                </section>


                <section class="history-detail-section">

                    <div class="history-section-title">

                        <div>
                            INTELLIGENCE & SÉCURITÉ
                        </div>

                        <span>
                            ANALYSE PHOENIX
                        </span>

                    </div>


                    <div class="history-security-panel">

                        <div class="history-threat-gauge">

                            <div>

                                <span>
                                    MENACE
                                </span>

                                <strong class="${escapeHtml(threat)}">
                                    ${escapeHtml(threat)}
                                </strong>

                            </div>


                            <div class="history-threat-track">

                                <span
                                    style="width: ${Math.min(
                                        100,
                                        Math.max(
                                            0,
                                            Number(
                                                record.threat_score
                                                ||
                                                0
                                            )
                                        )
                                    )}%"
                                ></span>

                            </div>

                        </div>


                        <div class="history-detail-grid">

                            ${detailField(
                                "Score menace",
                                `${
                                    Number(
                                        record.threat_score
                                        ||
                                        0
                                    )
                                } / 100`
                            )}

                            ${detailField(
                                "Statut",
                                displayValue(
                                    record.status
                                )
                            )}

                            ${detailField(
                                "Alertes associées",
                                displayValue(
                                    record.alerts,
                                    "0"
                                )
                            )}

                            ${detailField(
                                "Franchissements",
                                displayValue(
                                    record.crossings,
                                    "0"
                                )
                            )}

                        </div>

                    </div>

                </section>


                <section class="history-detail-section">

                    <div class="history-section-title">

                        <div>
                            PREUVES & MÉDIAS
                        </div>

                        <span>
                            DOSSIER FORENSIC
                        </span>

                    </div>


                    <div class="history-media-grid">

                        <article class="history-media-card">

                            <div class="history-media-placeholder">

                                <svg class="phoenix-icon">
                                    <use href="/static/icons/phoenix-ui.svg#icon-camera"></use>
                                </svg>

                            </div>

                            <div>

                                <strong>
                                    Capture véhicule
                                </strong>

                                <span>
                                    Aucune image associée à cet enregistrement
                                </span>

                            </div>

                        </article>


                        <article class="history-media-card">

                            <div class="history-media-placeholder">

                                <svg class="phoenix-icon">
                                    <use href="/static/icons/phoenix-ui.svg#icon-anpr"></use>
                                </svg>

                            </div>

                            <div>

                                <strong>
                                    Capture plaque
                                </strong>

                                <span>
                                    ${
                                        hasPlate(record)
                                        ?
                                        "Plaque connue, image non persistée"
                                        :
                                        "Aucune plaque exploitable enregistrée"
                                    }
                                </span>

                            </div>

                        </article>

                    </div>


                    <div class="history-evidence-status">

                        <span class="history-evidence-dot"></span>

                        <div>

                            <strong>
                                Captures de preuve
                            </strong>

                            <span>
                                Aucune preuve média persistée pour cet enregistrement.
                            </span>

                        </div>

                    </div>

                </section>


                <section class="history-detail-footer">

                    <div>

                        <span>
                            IDENTIFIANT PHOENIX
                        </span>

                        <code>
                            ${escapeHtml(
                                record.uuid || "—"
                            )}
                        </code>

                    </div>


                    <div class="history-persistence-badge">

                        <span></span>

                        SQLITE
                        ·
                        PERSISTANT

                    </div>

                </section>
            `;
        }


        async function openDetail(
            record
        ) {

            createDetailShell();


            const overlay =
                document.getElementById(
                    "history-detail-overlay"
                );


            const content =
                document.getElementById(
                    "history-detail-content"
                );


            overlay.classList.add(
                "open"
            );


            document.body.classList.add(
                "history-detail-open"
            );


            content.innerHTML = `

                <div class="history-detail-loading">

                    <span></span>

                    Chargement de la fiche Phoenix...

                </div>
            `;


            try {

                const response =
                    await fetch(

                        "/api/history/"
                        +
                        encodeURIComponent(
                            record.uuid
                        ),

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

                    window.location.replace(
                        "/login"
                    );

                    return;
                }


                if(!response.ok) {

                    throw new Error(
                        "HTTP "
                        +
                        response.status
                    );
                }


                const data =
                    await response.json();


                if(
                    data.success !== true
                    ||
                    !data.record
                ) {

                    throw new Error(
                        data.error
                        ||
                        "Enregistrement introuvable"
                    );
                }


                renderDetail(
                    data.record
                );

            }
            catch(error) {

                content.innerHTML = `

                    <div class="history-detail-error">

                        <strong>
                            Impossible d'ouvrir la fiche
                        </strong>

                        <span>
                            ${escapeHtml(
                                error.message
                            )}
                        </span>

                    </div>
                `;
            }
        }


        function filteredRecords() {

            const query =
                search.value
                .trim()
                .toLowerCase();


            const threat =
                threatFilter.value;


            const plate =
                plateFilter.value;


            return records.filter(
                record => {

                    const level =
                        String(
                            record.threat_level
                            ||
                            "UNKNOWN"
                        ).toUpperCase();


                    if(
                        threat !== "ALL"
                        &&
                        level !== threat
                    ) {

                        return false;
                    }


                    const platePresent =
                        hasPlate(
                            record
                        );


                    if(
                        plate
                        ===
                        "WITH_PLATE"
                        &&
                        !platePresent
                    ) {

                        return false;
                    }


                    if(
                        plate
                        ===
                        "WITHOUT_PLATE"
                        &&
                        platePresent
                    ) {

                        return false;
                    }


                    if(!query) {

                        return true;
                    }


                    return [

                        record.tracker_id,
                        record.label,
                        record.plate,
                        record.color,
                        record.brand,
                        record.model,
                        record.zone,
                        record.status,
                        record.threat_level

                    ]
                    .join(" ")
                    .toLowerCase()
                    .includes(
                        query
                    );

                }
            );
        }


        function render() {

            const visible =
                filteredRecords();


            list.replaceChildren();


            visible.forEach(
                record => {

                    const row =
                        document.createElement(
                            "div"
                        );


                    row.className =
                        "history-row";

                    row.dataset.vehicleUuid =
                        record.uuid || "";


                    row.tabIndex = 0;


                    row.setAttribute(
                        "role",
                        "button"
                    );


                    row.setAttribute(
                        "aria-label",
                        "Ouvrir la fiche historique"
                    );


                    row.title =
                        "Cliquer pour ouvrir la fiche complète";


                    const threat =
                        safeThreatClass(
                            record.threat_level
                        );


                    const plate =
                        String(
                            record.plate
                            ||
                            ""
                        ).trim();


                    row.innerHTML = `

                        <span class="history-date">
                            ${escapeHtml(
                                formatDate(
                                    record.last_seen
                                    ||
                                    record.created_at
                                )
                            )}
                        </span>

                        <span class="history-tracker">
                            ${escapeHtml(
                                record.tracker_id
                                ??
                                "—"
                            )}
                        </span>

                        <span>
                            ${escapeHtml(
                                record.label
                                ||
                                "—"
                            )}
                        </span>

                        <span class="history-plate ${plate ? "" : "empty"}">
                            ${escapeHtml(
                                plate
                                ||
                                "Non lue"
                            )}
                        </span>

                        <span>
                            ${escapeHtml(
                                record.zone
                                ||
                                "—"
                            )}
                        </span>

                        <span>
                            ${escapeHtml(
                                record.max_speed
                                ??
                                0
                            )}
                        </span>

                        <span class="history-threat ${escapeHtml(threat)}">
                            ${escapeHtml(threat)}
                        </span>

                        <span>
                            ${escapeHtml(
                                record.status
                                ||
                                "—"
                            )}
                        </span>
                    `;


                    row.addEventListener(
                        "click",
                        () => {

                            openDetail(
                                record
                            );

                        }
                    );


                    row.addEventListener(
                        "keydown",
                        event => {

                            if(
                                event.key
                                ===
                                "Enter"
                                ||
                                event.key
                                ===
                                " "
                            ) {

                                event.preventDefault();

                                openDetail(
                                    record
                                );
                            }

                        }
                    );


                    list.appendChild(
                        row
                    );

                }
            );


            empty.classList.toggle(
                "hidden",
                visible.length !== 0
            );
        }


        async function loadHistory() {

            try {

                const response =
                    await fetch(
                        "/api/history?limit=500",
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

                    window.location.replace(
                        "/login"
                    );

                    return;
                }


                if(!response.ok) {

                    throw new Error(
                        "HTTP "
                        +
                        response.status
                    );
                }


                const data =
                    await response.json();


                if(
                    data.success
                    !==
                    true
                ) {

                    throw new Error(
                        data.error
                        ||
                        "Réponse API invalide."
                    );
                }


                records =
                    Array.isArray(
                        data.records
                    )
                    ?
                    data.records
                    :
                    [];


                document.getElementById(
                    "history-total"
                ).textContent =
                    data.total ?? 0;


                document.getElementById(
                    "history-today"
                ).textContent =
                    data.today ?? 0;


                document.getElementById(
                    "history-plates"
                ).textContent =
                    data.plates ?? 0;


                document.getElementById(
                    "history-threats"
                ).textContent =
                    data.threats ?? 0;


                render();


                refreshTime.textContent =
                    "Actualisation : "
                    +
                    new Date()
                    .toLocaleTimeString(
                        "fr-FR"
                    );


                message.classList.add(
                    "hidden"
                );

            }
            catch(error) {

                message.textContent =
                    "Impossible de charger l'historique : "
                    +
                    error.message;


                message.classList.remove(
                    "hidden"
                );
            }
        }


        search.addEventListener(
            "input",
            render
        );


        threatFilter.addEventListener(
            "change",
            render
        );


        plateFilter.addEventListener(
            "change",
            render
        );


        createDetailShell();

        loadHistory();


        window.setInterval(
            loadHistory,
            15000
        );

    }
);
