/*
========================================================
PHOENIX VISION AI
Enterprise AI Alerts Console
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const list =
            document.getElementById(
                "alerts-list"
            );

        const empty =
            document.getElementById(
                "alerts-empty"
            );

        const message =
            document.getElementById(
                "alerts-message"
            );

        const search =
            document.getElementById(
                "alert-search"
            );

        const levelFilter =
            document.getElementById(
                "alert-level-filter"
            );

        const statusFilter =
            document.getElementById(
                "alert-status-filter"
            );

        const refreshTime =
            document.getElementById(
                "alerts-refresh-time"
            );


        let alerts = [];


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
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                }
            );

        }


        function filteredAlerts(){

            const query =
                search.value
                .trim()
                .toLowerCase();


            const level =
                levelFilter.value;


            const status =
                statusFilter.value;


            return alerts.filter(
                alert => {

                    const alertLevel =
                        String(
                            alert.level || ""
                        ).toUpperCase();


                    const alertStatus =
                        String(
                            alert.status || ""
                        ).toUpperCase();


                    if(
                        level !== "ALL"
                        &&
                        alertLevel !== level
                    ){

                        return false;

                    }


                    if(
                        status === "OPEN"
                        &&
                        ![
                            "ACTIVE",
                            "ACKNOWLEDGED"
                        ].includes(
                            alertStatus
                        )
                    ){

                        return false;

                    }


                    if(
                        status !== "OPEN"
                        &&
                        status !== "ALL"
                        &&
                        alertStatus !== status
                    ){

                        return false;

                    }


                    if(!query){

                        return true;

                    }


                    const searchable = [

                        alert.type,
                        alert.level,
                        alert.status,
                        alert.message,
                        alert.tracker_id,
                        alert.vehicle_uuid,
                        alert.threat_score

                    ]
                    .join(" ")
                    .toLowerCase();


                    return searchable.includes(
                        query
                    );

                }
            );

        }


        async function acknowledgeAlert(
            alertUuid
        ) {

            const response =
                await fetch(

                    "/api/alerts/"
                    +
                    encodeURIComponent(
                        alertUuid
                    )
                    +
                    "/acknowledge",

                    {
                        method:
                            "POST",

                        credentials:
                            "same-origin"
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


            await loadAlerts();

        }


        function render(){

            const visible =
                filteredAlerts();


            list.replaceChildren();


            visible.forEach(
                alert => {

                    const row =
                        document.createElement(
                            "div"
                        );


                    row.className =
                        "alert-row";


                    const level =
                        String(
                            alert.level || "HIGH"
                        ).toUpperCase();


                    const status =
                        String(
                            alert.status || "ACTIVE"
                        ).toUpperCase();


                    const buttonDisabled =
                        status !== "ACTIVE";


                    row.innerHTML = `

                        <span>
                            ${escapeHtml(formatTime(alert.timestamp))}
                        </span>

                        <span class="alert-level ${escapeHtml(level)}">
                            ${escapeHtml(level)}
                        </span>

                        <span class="alert-status ${escapeHtml(status)}">
                            ${escapeHtml(status)}
                        </span>

                        <span>
                            ${escapeHtml(alert.tracker_id ?? "—")}
                        </span>

                        <span class="alert-score">
                            ${escapeHtml(alert.threat_score ?? 0)}
                        </span>

                        <span
                            class="alert-message"
                            title="${escapeHtml(alert.message || "")}"
                        >
                            ${escapeHtml(alert.message || "—")}
                        </span>

                        <button
                            class="alert-action"
                            type="button"
                            data-alert="${escapeHtml(alert.uuid)}"
                            ${buttonDisabled ? "disabled" : ""}
                        >
                            ${
                                status === "ACTIVE"
                                ? "ACQUITTER"
                                : (
                                    status === "ACKNOWLEDGED"
                                    ? "ACQUITTÉE"
                                    : "RÉSOLUE"
                                )
                            }
                        </button>
                    `;


                    const action =
                        row.querySelector(
                            ".alert-action"
                        );


                    if(
                        action
                        &&
                        !buttonDisabled
                    ){

                        action.addEventListener(
                            "click",
                            async () => {

                                action.disabled =
                                    true;


                                try{

                                    await acknowledgeAlert(
                                        alert.uuid
                                    );

                                }
                                catch(error){

                                    message.textContent =
                                        "Impossible d'acquitter l'alerte : "
                                        +
                                        error.message;

                                    message.classList.remove(
                                        "hidden"
                                    );

                                    action.disabled =
                                        false;

                                }

                            }
                        );

                    }


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


        async function loadAlerts(){

            try{

                const response =
                    await fetch(
                        "/api/alerts?limit=500",
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


                alerts =
                    Array.isArray(
                        data.alerts
                    )
                    ?
                    data.alerts
                    :
                    [];


                document.getElementById(
                    "alerts-open"
                ).textContent =
                    data.open ?? 0;


                document.getElementById(
                    "alerts-high"
                ).textContent =
                    data.high ?? 0;


                document.getElementById(
                    "alerts-critical"
                ).textContent =
                    data.critical ?? 0;


                document.getElementById(
                    "alerts-ack"
                ).textContent =
                    data.acknowledged ?? 0;


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
                    "Impossible de charger les alertes : "
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


        statusFilter.addEventListener(
            "change",
            render
        );


        loadAlerts();


        window.setInterval(
            loadAlerts,
            10000
        );

    }
);
