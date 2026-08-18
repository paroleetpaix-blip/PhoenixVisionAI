/*
========================================================
PHOENIX VISION AI
Enterprise Events Console
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const list =
            document.getElementById(
                "events-list"
            );

        const empty =
            document.getElementById(
                "events-empty"
            );

        const message =
            document.getElementById(
                "events-message"
            );

        const search =
            document.getElementById(
                "event-search"
            );

        const levelFilter =
            document.getElementById(
                "event-level-filter"
            );

        const typeFilter =
            document.getElementById(
                "event-type-filter"
            );

        const refreshTime =
            document.getElementById(
                "events-refresh-time"
            );


        let events = [];


        function escapeHtml(
            value
        ) {

            const div =
                document.createElement(
                    "div"
                );

            div.textContent =
                String(
                    value ?? ""
                );

            return div.innerHTML;

        }


        function formatTime(
            value
        ) {

            if(!value){

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
            ){

                return "—";

            }


            return date.toLocaleTimeString(
                "fr-FR",
                {
                    hour:
                        "2-digit",

                    minute:
                        "2-digit",

                    second:
                        "2-digit"
                }
            );

        }


        function filteredEvents(){

            const query =
                search.value
                .trim()
                .toLowerCase();


            const level =
                levelFilter.value;


            const type =
                typeFilter.value;


            return events.filter(
                event => {

                    const eventLevel =
                        String(
                            event.level
                            ||
                            "INFO"
                        ).toUpperCase();


                    const eventType =
                        String(
                            event.type
                            ||
                            "EVENT"
                        ).toUpperCase();


                    if(
                        level !== "ALL"
                        &&
                        eventLevel !== level
                    ){

                        return false;

                    }


                    if(
                        type !== "ALL"
                        &&
                        eventType !== type
                    ){

                        return false;

                    }


                    if(!query){

                        return true;

                    }


                    const searchable = [

                        event.type,
                        event.level,
                        event.description,
                        event.tracker_id,
                        event.vehicle_uuid,
                        event.line_name,
                        event.direction

                    ]
                    .join(" ")
                    .toLowerCase();


                    return searchable.includes(
                        query
                    );

                }
            );

        }


        function render(){

            const visible =
                filteredEvents();


            list.replaceChildren();


            visible.forEach(
                event => {

                    const row =
                        document.createElement(
                            "div"
                        );


                    row.className =
                        "event-row";


                    const level =
                        String(
                            event.level
                            ||
                            "INFO"
                        ).toUpperCase();


                    row.innerHTML = `

                        <span class="event-time">
                            ${escapeHtml(formatTime(event.timestamp))}
                        </span>

                        <span class="event-type">
                            ${escapeHtml(event.type || "EVENT")}
                        </span>

                        <span class="event-level ${escapeHtml(level)}">
                            ${escapeHtml(level)}
                        </span>

                        <span>
                            ${escapeHtml(event.tracker_id ?? "—")}
                        </span>

                        <span
                            class="event-description"
                            title="${escapeHtml(event.description || "")}"
                        >
                            ${escapeHtml(event.description || "—")}
                        </span>
                    `;


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


        function rebuildTypeFilter(){

            const previous =
                typeFilter.value;


            const types = [

                ...new Set(

                    events.map(
                        event =>
                            String(
                                event.type
                                ||
                                "EVENT"
                            ).toUpperCase()
                    )

                )

            ].sort();


            typeFilter.innerHTML =
                '<option value="ALL">Tous types</option>';


            types.forEach(
                type => {

                    const option =
                        document.createElement(
                            "option"
                        );

                    option.value =
                        type;

                    option.textContent =
                        type;

                    typeFilter.appendChild(
                        option
                    );

                }
            );


            if(
                types.includes(
                    previous
                )
            ){

                typeFilter.value =
                    previous;

            }

        }


        async function loadEvents(){

            try{

                const response =
                    await fetch(
                        "/api/events?limit=500",
                        {
                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
                        }
                    );


                if(
                    response.status === 401
                ){

                    window.location.replace(
                        "/login"
                    );

                    return;

                }


                if(!response.ok){

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
                ){

                    throw new Error(
                        data.error
                        ||
                        "Réponse API invalide."
                    );

                }


                events =
                    Array.isArray(
                        data.events
                    )
                    ?
                    data.events
                    :
                    [];


                document.getElementById(
                    "events-total"
                ).textContent =
                    data.total ?? 0;


                document.getElementById(
                    "events-today"
                ).textContent =
                    data.today ?? 0;


                document.getElementById(
                    "events-warning"
                ).textContent =
                    data.warnings ?? 0;


                document.getElementById(
                    "events-critical"
                ).textContent =
                    data.critical ?? 0;


                rebuildTypeFilter();

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
            catch(error){

                message.textContent =
                    "Impossible de charger les événements : "
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


        levelFilter.addEventListener(
            "change",
            render
        );


        typeFilter.addEventListener(
            "change",
            render
        );


        loadEvents();


        window.setInterval(
            loadEvents,
            10000
        );

    }
);
