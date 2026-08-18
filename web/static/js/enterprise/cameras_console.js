/*
========================================================
PHOENIX VISION AI
Enterprise Camera Operations Console
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const grid =
            document.getElementById(
                "camera-console-grid"
            );

        const emptyState =
            document.getElementById(
                "camera-empty"
            );

        const message =
            document.getElementById(
                "camera-message"
            );

        const searchInput =
            document.getElementById(
                "camera-search-input"
            );

        const refreshButton =
            document.getElementById(
                "refresh-cameras"
            );

        const filterButtons =
            Array.from(
                document.querySelectorAll(
                    ".filter-button"
                )
            );

        const totalElement =
            document.getElementById(
                "camera-total"
            );

        const onlineElement =
            document.getElementById(
                "camera-online"
            );

        const connectingElement =
            document.getElementById(
                "camera-connecting"
            );

        const offlineElement =
            document.getElementById(
                "camera-offline"
            );

        const lastRefreshElement =
            document.getElementById(
                "last-refresh"
            );


        let cameras = [];

        let activeFilter =
            "ALL";


        function escapeHtml(
            value
        ) {

            const element =
                document.createElement(
                    "div"
                );

            element.textContent =
                String(
                    value ?? ""
                );

            return element.innerHTML;

        }


        function normalizeStatus(
            status
        ) {

            const value =
                String(
                    status || "OFFLINE"
                ).toUpperCase();


            if(
                value === "ONLINE"
                ||
                value === "CONNECTING"
                ||
                value === "OFFLINE"
            ){

                return value;

            }


            return "OFFLINE";

        }


        function statusLabel(
            status
        ) {

            switch(
                normalizeStatus(
                    status
                )
            ){

                case "ONLINE":

                    return "EN LIGNE";


                case "CONNECTING":

                    return "CONNEXION";


                default:

                    return "HORS LIGNE";

            }

        }


        function formatResolution(
            resolution
        ) {

            if(
                !Array.isArray(
                    resolution
                )
                ||
                resolution.length < 2
            ){

                return "—";

            }


            const width =
                Number(
                    resolution[0]
                ) || 0;

            const height =
                Number(
                    resolution[1]
                ) || 0;


            if(
                width <= 0
                ||
                height <= 0
            ){

                return "—";

            }


            return (
                width
                +
                " × "
                +
                height
            );

        }


        function createCameraCard(
            camera
        ) {

            const article =
                document.createElement(
                    "article"
                );


            const status =
                normalizeStatus(
                    camera.status
                );


            article.className =
                "camera-entry";

            article.dataset.status =
                status;


            const name =
                escapeHtml(
                    camera.name || "CAMÉRA"
                );

            const source =
                escapeHtml(
                    camera.source || "—"
                );

            const type =
                escapeHtml(
                    camera.type || "—"
                );

            const fps =
                Number(
                    camera.fps
                ) || 0;

            const resolution =
                escapeHtml(
                    formatResolution(
                        camera.resolution
                    )
                );

            const reconnects =
                Number(
                    camera.reconnects
                ) || 0;

            const encodedName =
                encodeURIComponent(
                    camera.name || ""
                );


            article.innerHTML = `

                <div class="camera-entry-header">

                    <div class="camera-name">
                        ${name}
                    </div>

                    <div class="camera-status">

                        <span
                            class="camera-status-dot"
                        ></span>

                        ${statusLabel(status)}

                    </div>

                </div>


                <div class="camera-entry-body">

                    <div class="camera-preview-icon">

                        <svg class="phoenix-icon">
                            <use href="/static/icons/phoenix-ui.svg#icon-camera"></use>
                        </svg>

                    </div>

                    <div class="camera-signal">

                        ${
                            status === "ONLINE"
                            ? "FLUX DISPONIBLE"
                            : (
                                status === "CONNECTING"
                                ? "CONNEXION..."
                                : "SIGNAL INDISPONIBLE"
                            )
                        }

                    </div>

                </div>


                <div class="camera-entry-footer">

                    <div class="camera-meta-grid">

                        <div class="camera-meta">

                            <span>
                                TYPE
                            </span>

                            <strong>
                                ${type}
                            </strong>

                        </div>


                        <div class="camera-meta">

                            <span>
                                RÉSOLUTION
                            </span>

                            <strong>
                                ${resolution}
                            </strong>

                        </div>


                        <div class="camera-meta">

                            <span>
                                FPS
                            </span>

                            <strong>
                                ${fps}
                            </strong>

                        </div>


                        <div class="camera-meta">

                            <span>
                                RECONNEXIONS
                            </span>

                            <strong>
                                ${reconnects}
                            </strong>

                        </div>

                    </div>


                    <div
                        class="camera-meta"
                        style="margin-bottom:10px"
                    >

                        <span>
                            SOURCE
                        </span>

                        <strong
                            title="${source}"
                        >
                            ${source}
                        </strong>

                    </div>


                    <a
                        class="camera-open"
                        href="/camera/${encodedName}"
                    >

                        <svg class="phoenix-icon">
                            <use href="/static/icons/phoenix-ui.svg#icon-camera"></use>
                        </svg>

                        OUVRIR LA CAMÉRA

                    </a>

                </div>
            `;


            return article;

        }


        function filteredCameras(){

            const search =
                String(
                    searchInput.value || ""
                )
                .trim()
                .toLowerCase();


            return cameras.filter(
                camera => {

                    const status =
                        normalizeStatus(
                            camera.status
                        );


                    if(
                        activeFilter !== "ALL"
                        &&
                        status !== activeFilter
                    ){

                        return false;

                    }


                    if(
                        !search
                    ){

                        return true;

                    }


                    const searchable = [

                        camera.name,
                        camera.type,
                        camera.source,
                        camera.uuid

                    ]
                    .join(" ")
                    .toLowerCase();


                    return searchable.includes(
                        search
                    );

                }
            );

        }


        function render(){

            const visible =
                filteredCameras();


            grid.replaceChildren();


            visible.forEach(
                camera => {

                    grid.appendChild(
                        createCameraCard(
                            camera
                        )
                    );

                }
            );


            emptyState.classList.toggle(
                "hidden",
                visible.length !== 0
            );

        }


        function updateSummary(
            payload
        ) {

            totalElement.textContent =
                payload.total ?? 0;

            onlineElement.textContent =
                payload.online ?? 0;

            connectingElement.textContent =
                payload.connecting ?? 0;

            offlineElement.textContent =
                payload.offline ?? 0;

        }


        function showMessage(
            text
        ) {

            message.textContent =
                text;

            message.classList.remove(
                "hidden"
            );

        }


        function hideMessage(){

            message.classList.add(
                "hidden"
            );

        }


        function updateRefreshTime(){

            const now =
                new Date();


            lastRefreshElement.textContent =
                "Actualisation : "
                +
                now.toLocaleTimeString(
                    "fr-FR",
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    }
                );

        }


        async function loadCameras(){

            hideMessage();


            refreshButton.disabled =
                true;


            try{

                const response =
                    await fetch(
                        "/api/cameras",
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


                if(
                    !response.ok
                ){

                    throw new Error(
                        "HTTP "
                        +
                        response.status
                    );

                }


                const payload =
                    await response.json();


                if(
                    payload.success !== true
                ){

                    throw new Error(
                        payload.error
                        ||
                        "Réponse API invalide."
                    );

                }


                cameras =
                    Array.isArray(
                        payload.cameras
                    )
                    ?
                    payload.cameras
                    :
                    [];


                updateSummary(
                    payload
                );


                render();


                updateRefreshTime();


                if(
                    payload.engine_available === false
                ){

                    showMessage(
                        "Le moteur Phoenix n'est pas encore disponible."
                    );

                }
                else if(
                    payload.camera_manager_available === false
                ){

                    showMessage(
                        "Le gestionnaire de caméras n'est pas disponible."
                    );

                }

            }
            catch(
                error
            ){

                cameras = [];

                updateSummary({
                    total: 0,
                    online: 0,
                    connecting: 0,
                    offline: 0
                });

                render();

                showMessage(
                    "Impossible de charger les caméras : "
                    +
                    error.message
                );

            }
            finally{

                refreshButton.disabled =
                    false;

            }

        }


        filterButtons.forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        filterButtons.forEach(
                            item => {

                                item.classList.remove(
                                    "active"
                                );

                            }
                        );


                        button.classList.add(
                            "active"
                        );


                        activeFilter =
                            button.dataset.filter
                            ||
                            "ALL";


                        render();

                    }
                );

            }
        );


        searchInput.addEventListener(
            "input",
            render
        );


        refreshButton.addEventListener(
            "click",
            loadCameras
        );


        loadCameras();


        window.setInterval(
            loadCameras,
            10000
        );

    }
);
