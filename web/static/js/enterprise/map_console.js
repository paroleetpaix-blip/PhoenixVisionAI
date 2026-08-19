/*
========================================================
PHOENIX VISION AI
Enterprise Operational Map
v4.6.2
========================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    () => {


        const cameraLayer =
            document.getElementById(
                "map-camera-layer"
            );


        const zoneLayer =
            document.getElementById(
                "map-zone-layer"
            );


        const zoneList =
            document.getElementById(
                "map-zone-list"
            );


        const emptyState =
            document.getElementById(
                "map-empty"
            );


        const cameraToggle =
            document.getElementById(
                "map-toggle-cameras"
            );


        const zoneToggle =
            document.getElementById(
                "map-toggle-zones"
            );


        const geographicButton =
            document.getElementById(
                "map-geographic-button"
            );


        let selectedCameraUuid = null;


        function text(
            value,
            fallback="Non configuré"
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


        function setText(
            id,
            value,
            fallback="0"
        ) {

            const element =
                document.getElementById(
                    id
                );


            if(element) {

                element.textContent =
                    text(
                        value,
                        fallback
                    );

            }

        }


        function statusClass(
            status
        ) {

            const normalized =
                String(
                    status || ""
                ).toLowerCase();


            if(normalized === "online") {

                return "online";

            }


            if(normalized === "connecting") {

                return "connecting";

            }


            return "offline";

        }


        function selectCamera(
            camera
        ) {

            selectedCameraUuid =
                camera.uuid;


            const detailPanel =
                document.querySelector(
                    ".map-detail-panel"
                );


            if(detailPanel) {

                detailPanel.classList.remove(
                    "selection-changed"
                );

                void detailPanel.offsetWidth;

                detailPanel.classList.add(
                    "selection-changed"
                );

            }


            document
                .querySelectorAll(
                    ".map-camera-node"
                )
                .forEach(
                    node => {

                        node.classList.toggle(
                            "selected",
                            node.dataset.uuid
                            ===
                            camera.uuid
                        );

                    }
                );


            setText(
                "map-detail-name",
                camera.name,
                "CAMÉRA"
            );


            const status =
                document.getElementById(
                    "map-detail-status"
                );


            status.textContent =
                text(
                    camera.status,
                    "INCONNU"
                ).toUpperCase();


            status.className =
                "map-detail-status "
                +
                statusClass(
                    camera.status
                );


            setText(
                "map-detail-type",
                camera.type,
                "—"
            );


            setText(
                "map-detail-source",
                camera.source_type,
                "—"
            );


            setText(
                "map-detail-site",
                camera.site,
                "Non configuré"
            );


            setText(
                "map-detail-location",
                camera.location_name,
                "Non configuré"
            );


            setText(
                "map-detail-city",
                camera.city,
                "Non configurée"
            );


            setText(
                "map-detail-gps",
                camera.gps_configured
                ?
                "Configuré"
                :
                "Non configuré"
            );


            setText(
                "map-detail-latitude",
                camera.latitude,
                "—"
            );


            setText(
                "map-detail-longitude",
                camera.longitude,
                "—"
            );

        }


        function renderCameras(
            cameras
        ) {

            cameraLayer.innerHTML = "";


            emptyState.hidden =
                cameras.length > 0;


            cameras.forEach(
                camera => {

                    const node =
                        document.createElement(
                            "button"
                        );


                    node.type =
                        "button";


                    node.className =
                        "map-camera-node";


                    node.dataset.uuid =
                        camera.uuid || "";


                    const status =
                        statusClass(
                            camera.status
                        );


                    node.innerHTML = `

                        <div class="map-camera-node-head">

                            <span
                                class="map-camera-status-dot ${status}"
                            ></span>

                            <strong>
                                ${text(camera.name, "CAMÉRA")}
                            </strong>

                        </div>

                        <small>
                            ${text(camera.type, "INCONNU")}
                            ·
                            ${text(camera.status, "INCONNU")}
                        </small>

                        <div
                            class="map-camera-gps ${
                                camera.gps_configured
                                ?
                                "configured"
                                :
                                ""
                            }"
                        >

                            ${
                                camera.gps_configured
                                ?
                                "GPS CONFIGURÉ"
                                :
                                "GPS NON CONFIGURÉ"
                            }

                        </div>
                    `;


                    node.addEventListener(
                        "click",
                        () => {

                            selectCamera(
                                camera
                            );

                        }
                    );


                    cameraLayer.appendChild(
                        node
                    );

                }
            );


            if(cameras.length > 0) {

                const selected =
                    cameras.find(
                        camera =>
                            camera.uuid
                            ===
                            selectedCameraUuid
                    )
                    ||
                    cameras[0];


                selectCamera(
                    selected
                );

            }

        }


        function renderZones(
            zones
        ) {

            zoneList.innerHTML = "";


            if(zones.length === 0) {

                const empty =
                    document.createElement(
                        "div"
                    );


                empty.className =
                    "map-zone-item";


                empty.innerHTML = `

                    <strong>
                        AUCUNE ZONE
                    </strong>

                    <span>
                        Aucune zone vidéo active
                    </span>
                `;


                zoneList.appendChild(
                    empty
                );


                return;

            }


            zones.forEach(
                zone => {

                    const item =
                        document.createElement(
                            "div"
                        );


                    item.className =
                        "map-zone-item";


                    item.innerHTML = `

                        <strong>
                            ${text(zone.name, "ZONE")}
                        </strong>

                        <span>
                            ${text(
                                zone.coordinate_system,
                                "VIDEO_FRAME"
                            )}
                            ·
                            [
                            ${text(zone.x1, "—")},
                            ${text(zone.y1, "—")}
                            →
                            ${text(zone.x2, "—")},
                            ${text(zone.y2, "—")}
                            ]
                        </span>
                    `;


                    zoneList.appendChild(
                        item
                    );

                }
            );

        }


        function renderStats(
            data
        ) {

            setText(
                "map-total-cameras",
                data.total_cameras
            );

            setText(
                "map-online",
                data.online
            );

            setText(
                "map-zones",
                data.zones_total
            );

            setText(
                "map-gps",
                data.gps_configured
            );

            setText(
                "map-alerts",
                data.open_alerts
            );


            const mode =
                document.getElementById(
                    "map-mode"
                );


            const notice =
                document.getElementById(
                    "map-gps-notice"
                );


            if(data.geographic_mode) {

                mode.textContent =
                    "MODE GÉOGRAPHIQUE";


                notice.textContent =
                    "Coordonnées GPS disponibles. "
                    +
                    "La couche géographique peut être activée.";


                geographicButton.disabled =
                    false;

            }
            else {

                mode.textContent =
                    "MODE TOPOLOGIQUE";


                notice.textContent =
                    "GPS NON CONFIGURÉ · "
                    +
                    "Cette vue représente l'architecture "
                    +
                    "opérationnelle du système et non "
                    +
                    "une position géographique réelle.";


                geographicButton.disabled =
                    true;

            }

        }


        async function loadMap() {

            try {

                const response =
                    await fetch(
                        "/api/map",
                        {
                            credentials:
                                "same-origin",

                            cache:
                                "no-store"
                        }
                    );


                if(response.status === 401) {

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


                renderStats(
                    data
                );


                renderCameras(
                    Array.isArray(
                        data.cameras
                    )
                    ?
                    data.cameras
                    :
                    []
                );


                renderZones(
                    Array.isArray(
                        data.zones
                    )
                    ?
                    data.zones
                    :
                    []
                );

            }
            catch(error) {

                console.error(
                    "Phoenix Map:",
                    error
                );

            }

        }


        cameraToggle.addEventListener(
            "click",
            () => {

                const hidden =
                    cameraLayer.classList.toggle(
                        "layer-hidden"
                    );


                cameraToggle.classList.toggle(
                    "active",
                    !hidden
                );

            }
        );


        zoneToggle.addEventListener(
            "click",
            () => {

                const hidden =
                    zoneLayer.classList.toggle(
                        "layer-hidden"
                    );


                zoneToggle.classList.toggle(
                    "active",
                    !hidden
                );

            }
        );


        loadMap();


        window.setInterval(
            loadMap,
            10000
        );


    }
);
