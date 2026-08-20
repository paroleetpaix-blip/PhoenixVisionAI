/*
========================================================
PHOENIX VISION AI
Console Plaques / LAPI
v4.7.3
========================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    () => {


        const list =
            document.getElementById(
                "plates-list"
            );


        const empty =
            document.getElementById(
                "plates-empty"
            );


        const input =
            document.getElementById(
                "plates-search-input"
            );


        const searchButton =
            document.getElementById(
                "plates-search-button"
            );


        const filters =
            Array.from(
                document.querySelectorAll(
                    ".plates-filter"
                )
            );


        let records = [];

        let currentFilter =
            "ALL";

        let selectedUuid =
            null;


        function safe(
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

            return safe(
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

                return safe(
                    value
                );

            }


            return date.toLocaleString(
                "fr-FR"
            );

        }


        function confidence(
            value
        ) {

            const number =
                Number(
                    value
                );


            if(
                !Number.isFinite(
                    number
                )
                ||
                number <= 0
            ) {

                return "—";

            }


            return (
                number.toFixed(
                    1
                )
                .replace(
                    ".",
                    ","
                )
                +
                " %"
            );

        }


        function statusClass(
            status
        ) {

            const normalized =
                safe(
                    status,
                    ""
                )
                .toUpperCase();


            if(
                normalized
                ===
                "VALIDATED"
            ) {

                return "success";

            }


            if(
                normalized
                ===
                "LOW_CONFIDENCE"
                ||
                normalized
                ===
                "INVALID_TEXT"
            ) {

                return "warning";

            }


            return "neutral";

        }


        function statusLabel(
            record
        ) {

            return safe(
                record
                .plate_status_label,
                "NON DÉTECTÉE"
            );

        }


        function isReview(
            record
        ) {

            const status =
                safe(
                    record.plate_status,
                    ""
                )
                .toUpperCase();


            return (
                status
                ===
                "LOW_CONFIDENCE"

                ||

                status
                ===
                "INVALID_TEXT"
            );

        }


        function filteredRecords() {

            if(
                currentFilter
                ===
                "ALL"
            ) {

                return records;

            }


            if(
                currentFilter
                ===
                "REVIEW"
            ) {

                return records.filter(
                    isReview
                );

            }


            return records.filter(
                record =>

                    safe(
                        record.plate_status,
                        ""
                    )
                    .toUpperCase()
                    ===
                    currentFilter

            );

        }


        function renderStats(
            data
        ) {

            const stats =
                data.stats || {};


            document.getElementById(
                "plates-total"
            ).textContent =
                stats.plates_detected
                ??
                0;


            document.getElementById(
                "plates-validated"
            ).textContent =
                stats.validated
                ??
                0;


            document.getElementById(
                "plates-review"
            ).textContent =
                stats.to_review
                ??
                0;


            const average =
                Number(
                    stats.average_confidence
                );


            document.getElementById(
                "plates-confidence"
            ).textContent =
                (
                    Number.isFinite(
                        average
                    )
                    &&
                    average > 0
                )
                ?
                average.toFixed(
                    1
                )
                .replace(
                    ".",
                    ","
                )
                +
                " %"
                :
                "—";


            const engine =
                data.engine || {};


            const box =
                document.getElementById(
                    "lapi-engine-status"
                );


            const label =
                box.querySelector(
                    "strong"
                );


            if(
                engine.ocr_available
                ===
                true
            ) {

                box.className =
                    "plates-engine-status online";

                label.textContent =
                    "EN LIGNE";

            }
            else {

                box.className =
                    "plates-engine-status offline";

                label.textContent =
                    "OCR INDISPONIBLE";

            }

        }


        function renderList() {

            const visible =
                filteredRecords();


            list.innerHTML =
                "";


            empty.hidden =
                visible.length > 0;


            document.getElementById(
                "plates-result-count"
            ).textContent =
                visible.length
                +
                (
                    visible.length > 1
                    ?
                    " résultats"
                    :
                    " résultat"
                );


            visible.forEach(
                record => {


                    const row =
                        document.createElement(
                            "button"
                        );


                    row.type =
                        "button";


                    row.className =
                        "plates-row";


                    row.dataset.uuid =
                        record.uuid || "";


                    if(
                        record.uuid
                        ===
                        selectedUuid
                    ) {

                        row.classList.add(
                            "selected"
                        );

                    }


                    row.innerHTML = `

                        <span
                            class="plates-number"
                        >
                            ${escapeHtml(
                                record.plate
                                ||
                                record.plate_raw
                                ||
                                "—"
                            )}
                        </span>

                        <span
                            class="plates-confidence"
                        >
                            ${escapeHtml(
                                confidence(
                                    record.plate_confidence
                                )
                            )}
                        </span>

                        <span>

                            <span
                                class="phx-status ${
                                    statusClass(
                                        record.plate_status
                                    )
                                }"
                            >
                                ${escapeHtml(
                                    statusLabel(
                                        record
                                    )
                                )}
                            </span>

                        </span>

                        <span>
                            ${escapeHtml(
                                record.last_camera
                                ||
                                "—"
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
                                formatDate(
                                    record.plate_last_seen
                                    ||
                                    record.last_seen
                                )
                            )}
                        </span>
                    `;


                    row.addEventListener(
                        "click",
                        () => {

                            selectRecord(
                                record
                            );

                        }
                    );


                    list.appendChild(
                        row
                    );

                }
            );

        }


        function selectRecord(
            record
        ) {

            selectedUuid =
                record.uuid;


            document
                .querySelectorAll(
                    ".plates-row"
                )
                .forEach(
                    row => {

                        row.classList.toggle(
                            "selected",
                            row.dataset.uuid
                            ===
                            selectedUuid
                        );

                    }
                );


            document.getElementById(
                "plates-detail-plate"
            ).textContent =
                safe(
                    record.plate
                    ||
                    record.plate_raw
                );


            const badge =
                document.getElementById(
                    "plates-detail-status"
                );


            badge.textContent =
                statusLabel(
                    record
                );


            badge.className =
                "phx-status "
                +
                statusClass(
                    record.plate_status
                );


            const score =
                Number(
                    record.plate_confidence
                );


            document.getElementById(
                "plates-detail-confidence"
            ).textContent =
                confidence(
                    score
                );


            document.getElementById(
                "plates-confidence-bar"
            ).style.width =
                (
                    Number.isFinite(
                        score
                    )
                    ?
                    Math.max(
                        0,
                        Math.min(
                            100,
                            score
                        )
                    )
                    :
                    0
                )
                +
                "%";


            document.getElementById(
                "plates-detail-raw"
            ).textContent =
                safe(
                    record.plate_raw
                );


            document.getElementById(
                "plates-detail-last-seen"
            ).textContent =
                formatDate(
                    record.plate_last_seen
                    ||
                    record.last_seen
                );


            document.getElementById(
                "plates-detail-camera"
            ).textContent =
                safe(
                    record.last_camera
                );


            document.getElementById(
                "plates-detail-zone"
            ).textContent =
                safe(
                    record.zone
                );


            document.getElementById(
                "plates-detail-type"
            ).textContent =
                safe(
                    record.label
                );


            document.getElementById(
                "plates-detail-tracker"
            ).textContent =
                safe(
                    record.tracker_id
                );


            document.getElementById(
                "plates-detail-uuid"
            ).textContent =
                safe(
                    record.uuid
                );


            const historyButton =
                document.getElementById(
                    "plates-history-button"
                );


            historyButton.disabled =
                !record.uuid;


            historyButton.onclick =
                () => {

                    window.location.href =
                        "/history";

                };

        }


        async function loadRecent() {

            try {

                const response =
                    await fetch(
                        "/api/anpr?limit=250",
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
                    return;
                }


                const data =
                    await response.json();


                if(
                    data.success
                    !==
                    true
                ) {

                    return;

                }


                records =
                    Array.isArray(
                        data.records
                    )
                    ?
                    data.records
                    :
                    [];


                renderStats(
                    data
                );


                renderList();


                document.getElementById(
                    "plates-last-refresh"
                ).textContent =
                    "Actualisé à "
                    +
                    new Date()
                    .toLocaleTimeString(
                        "fr-FR"
                    );

            }
            catch(error) {

                console.error(
                    "Phoenix LAPI:",
                    error
                );

            }

        }


        function renderForensic(
            summary
        ) {

            summary =
                summary || {};


            document.getElementById(
                "plates-forensic-occurrences"
            ).textContent =
                summary.occurrences
                ??
                0;


            document.getElementById(
                "plates-forensic-confidence"
            ).textContent =
                confidence(
                    summary.max_confidence
                );


            document.getElementById(
                "plates-forensic-first"
            ).textContent =
                formatDate(
                    summary.first_detection
                );


            document.getElementById(
                "plates-forensic-last"
            ).textContent =
                formatDate(
                    summary.last_detection
                );


            const cameras =
                Array.isArray(
                    summary.cameras
                )
                ?
                summary.cameras
                :
                [];


            document.getElementById(
                "plates-forensic-cameras"
            ).textContent =
                cameras.length
                ?
                cameras.join(
                    " · "
                )
                :
                "—";


            const zones =
                Array.isArray(
                    summary.zones
                )
                ?
                summary.zones
                :
                [];


            document.getElementById(
                "plates-forensic-zones"
            ).textContent =
                zones.length
                ?
                zones.join(
                    " · "
                )
                :
                "—";

        }


        function resetForensic() {

            renderForensic(
                {
                    occurrences: 0,
                    max_confidence: 0,
                    first_detection: null,
                    last_detection: null,
                    cameras: [],
                    zones: []
                }
            );

        }


        async function searchPlate() {

            const query =
                input.value.trim();


            if(
                query.length < 3
            ) {

                input.focus();

                return;

            }


            searchButton.disabled =
                true;


            try {

                const response =
                    await fetch(
                        "/api/anpr/forensic?plate="
                        +
                        encodeURIComponent(
                            query
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

                    records = [];

                    renderList();

                    resetForensic();

                    return;

                }


                const data =
                    await response.json();


                records =
                    Array.isArray(
                        data.records
                    )
                    ?
                    data.records
                    :
                    [];


                currentFilter =
                    "ALL";


                filters.forEach(
                    button => {

                        button.classList.toggle(
                            "active",
                            button.dataset.filter
                            ===
                            "ALL"
                        );

                    }
                );


                renderForensic(
                    data.summary
                );


                renderList();


                const resetButton =
                    document.getElementById(
                        "plates-search-reset"
                    );


                resetButton.hidden =
                    false;


                document.querySelector(
                    ".plates-list-panel"
                ).classList.add(
                    "plates-search-active"
                );


                if(
                    records.length > 0
                ) {

                    selectRecord(
                        records[0]
                    );

                }
                else {

                    selectedUuid = null;


                    document.getElementById(
                        "plates-detail-plate"
                    ).textContent =
                        data.normalized
                        ||
                        query.toUpperCase();


                    const badge =
                        document.getElementById(
                            "plates-detail-status"
                        );


                    badge.textContent =
                        "AUCUNE CORRESPONDANCE";


                    badge.className =
                        "phx-status neutral";


                    document.getElementById(
                        "plates-history-button"
                    ).disabled =
                        true;

                }

            }
            finally {

                searchButton.disabled =
                    false;

            }

        }


        async function resetSearch() {

            input.value =
                "";


            selectedUuid =
                null;


            resetForensic();


            document.getElementById(
                "plates-search-reset"
            ).hidden =
                true;


            document.querySelector(
                ".plates-list-panel"
            ).classList.remove(
                "plates-search-active"
            );


            await loadRecent();

        }



        filters.forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        currentFilter =
                            button.dataset.filter;


                        filters.forEach(
                            item => {

                                item.classList.toggle(
                                    "active",
                                    item === button
                                );

                            }
                        );


                        renderList();

                    }
                );

            }
        );


        searchButton.addEventListener(
            "click",
            searchPlate
        );


        document.getElementById(
            "plates-search-reset"
        ).addEventListener(
            "click",
            resetSearch
        );


        input.addEventListener(
            "keydown",
            event => {

                if(
                    event.key
                    ===
                    "Enter"
                ) {

                    searchPlate();

                }

            }
        );


        loadRecent();


        window.setInterval(
            loadRecent,
            15000
        );


    }
);
