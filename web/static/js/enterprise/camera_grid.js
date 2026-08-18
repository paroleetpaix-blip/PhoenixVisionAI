/*
========================================================
PHOENIX VISION AI
Enterprise Dashboard Controller
========================================================
*/


document.addEventListener(
    "DOMContentLoaded",
    () => {


        const cameraGrid =
            document.getElementById(
                "camera-grid"
            );


        const cameraOnlineCount =
            document.getElementById(
                "camera-online-count"
            );


        const topbarCameraCount =
            document.getElementById(
                "topbar-camera-count"
            );


        const systemCameras =
            document.getElementById(
                "system-cameras"
            );


        const cameraIndicator =
            document.getElementById(
                "camera-indicator"
            );


        const currentTime =
            document.getElementById(
                "current-time"
            );


        const currentDate =
            document.getElementById(
                "current-date"
            );


        const fullscreenButton =
            document.getElementById(
                "fullscreen-button"
            );


        const topbarUsername =
            document.getElementById(
                "topbar-username"
            );


        const topbarRole =
            document.getElementById(
                "topbar-role"
            );


        const topbarAvatar =
            document.getElementById(
                "topbar-user-avatar"
            );


        const sidebarUsername =
            document.getElementById(
                "sidebar-username"
            );


        const sidebarRole =
            document.getElementById(
                "sidebar-role"
            );


        const sidebarAvatar =
            document.getElementById(
                "sidebar-avatar"
            );


        const eventsList =
            document.getElementById(
                "events-list"
            );


        const eventsCount =
            document.getElementById(
                "events-count"
            );

        const vehiclePlate =
            document.getElementById(
                "vehicle-plate"
            );


        const vehicleType =
            document.getElementById(
                "vehicle-type"
            );


        const vehicleConfidence =
            document.getElementById(
                "vehicle-confidence"
            );


        const vehicleTrackerId =
            document.getElementById(
                "vehicle-tracker-id"
            );


        const vehicleZone =
            document.getElementById(
                "vehicle-zone"
            );


        const vehicleSpeed =
            document.getElementById(
                "vehicle-speed"
            );


        const vehicleDirection =
            document.getElementById(
                "vehicle-direction"
            );


        const vehicleThreat =
            document.getElementById(
                "vehicle-threat"
            );


        const vehiclePanelStatus =
            document.getElementById(
                "vehicle-panel-status"
            );


        let vehicleCameraName =
            "CAM01";


        /*
        ====================================================
        OUTILS
        ====================================================
        */


        function createInitials(
            username
        ){

            if(!username){

                return "OP";

            }


            const clean =
                username
                    .trim()
                    .toUpperCase();


            if(clean.length <= 2){

                return clean;

            }


            return clean.substring(
                0,
                2
            );

        }



        function formatRole(
            role
        ){

            const labels = {

                ADMIN:
                    "Administrateur",

                OPERATOR:
                    "Opérateur",

                SUPERVISOR:
                    "Superviseur",

                ANALYST:
                    "Analyste"

            };


            return labels[
                role
            ]
            ||
            role
            ||
            "Utilisateur";

        }

        function applyUserAvatar(
            element,
            photoUrl,
            initials
        ){

            if(!element){

                return;

            }


            element.textContent =
                initials;


            element.style.backgroundImage =
                "none";


            element.classList.remove(
                "has-photo"
            );


            if(!photoUrl){

                return;

            }


            const image =
                new Image();


            image.onload =
                () => {

                    element.textContent =
                        "";


                    element.style.backgroundImage =
                        `url("${photoUrl}")`;


                    element.classList.add(
                        "has-photo"
                    );

                };


            image.onerror =
                () => {

                    element.textContent =
                        initials;

                };


            image.src =
                photoUrl;

        }



        /*
        ====================================================
        UTILISATEUR
        ====================================================
        */


        async function loadCurrentUser(){

    try{

        const response =
            await fetch(
                "/api/session/me",
                {

                    credentials:
                        "same-origin"

                }
            );


        if(!response.ok){

            window.location.replace(
                "/login"
            );

            return;

        }


        const data =
            await response.json();


        const username =
            data.username
            ||
            "Utilisateur";

        const displayName =
            data.display_name
            ||
            username;


        const photoUrl =
            data.photo_url
            ||
            null;


        const role =
            (
                data.role
                ||
                "OPERATOR"
            )
            .toUpperCase();


        const displayRole =
            formatRole(
                role
            );


        const initials =
            createInitials(
                username
            );


        if(topbarUsername){

            topbarUsername.textContent =
                username;

        }


        if(topbarRole){

            topbarRole.textContent =
                role;

        }


        applyUserAvatar(

            topbarAvatar,

            photoUrl,

            initials

        );


        if(sidebarUsername){

            sidebarUsername.textContent =
                displayName;

        }


        if(sidebarRole){

            sidebarRole.textContent =
                role;

        }


        applyUserAvatar(

            sidebarAvatar,

            photoUrl,

            initials

        );


        document
            .querySelectorAll(
                ".admin-only"
            )
            .forEach(
                element => {

                    element.style.display =
                        role === "ADMIN"
                        ?
                        ""
                        :
                        "none";

                }
            );

    }

    catch(error){

        console.error(
            "Phoenix Session:",
            error
        );

    }

}



        /*
        ====================================================
        HORLOGE
        ====================================================
        */


        function updateClock(){

            const now =
                new Date();


            if(currentTime){

                currentTime.textContent =
                    now.toLocaleTimeString(
                        "fr-FR",
                        {

                            hour:
                                "2-digit",

                            minute:
                                "2-digit"

                        }
                    );

            }


            if(currentDate){

                currentDate.textContent =
                    now.toLocaleDateString(
                        "fr-FR",
                        {

                            weekday:
                                "short",

                            day:
                                "2-digit",

                            month:
                                "short",

                            year:
                                "numeric"

                        }
                    );

            }

        }



        /*
        ====================================================
        CAMÉRA CARD
        ====================================================
        */


        function createCameraCard(
            camera
        ){

            const card =
                document.createElement(
                    "article"
                );


            const online =
                camera.status
                ===
                "ONLINE";


            card.className =
                online
                ?
                "camera-card online"
                :
                "camera-card offline";


            card.dataset.camera =
                camera.name;


            const preview =
                document.createElement(
                    "div"
                );


            preview.className =
                "camera-preview";


            if(!online){

                const noSignal =
                    document.createElement(
                        "div"
                    );


                noSignal.className =
                    "camera-no-signal";


                noSignal.textContent =
                    "SIGNAL INDISPONIBLE";


                preview.appendChild(
                    noSignal
                );

            }


            const top =
                document.createElement(
                    "div"
                );


            top.className =
                "camera-overlay-top";


            const name =
                document.createElement(
                    "span"
                );


            name.className =
                "camera-name";


            name.textContent =
                camera.name;


            const status =
                document.createElement(
                    "span"
                );


            status.className =
                online
                ?
                "camera-status online"
                :
                "camera-status offline";


            const dot =
                document.createElement(
                    "span"
                );


            dot.className =
                "camera-status-dot";


            const statusText =
                document.createElement(
                    "span"
                );


            statusText.textContent =
                online
                ?
                "ONLINE"
                :
                "OFFLINE";


            status.appendChild(
                dot
            );


            status.appendChild(
                statusText
            );


            top.appendChild(
                name
            );


            top.appendChild(
                status
            );


            const bottom =
                document.createElement(
                    "div"
                );


            bottom.className =
                "camera-overlay-bottom";


            const location =
                document.createElement(
                    "span"
                );


            location.className =
                "camera-location";


            location.textContent =
                camera.location
                ||
                "Localisation inconnue";


            const fullscreenIcon =
                document.createElement(
                    "span"
                );


            fullscreenIcon.className =
                "camera-fullscreen-icon";


            fullscreenIcon.textContent =
                "⛶";


            bottom.appendChild(
                location
            );


            bottom.appendChild(
                fullscreenIcon
            );


            card.appendChild(
                preview
            );


            card.appendChild(
                top
            );


            card.appendChild(
                bottom
            );


            card.addEventListener(
                "click",
                () => {

                    window.location.href =
                        "/camera/"
                        +
                        encodeURIComponent(
                            camera.name
                        );

                }
            );


            return card;

        }



        /*
        ====================================================
        CHARGEMENT CAMÉRAS
        ====================================================
        */


        async function loadCameras(){

            if(!cameraGrid){

                return;

            }


            try{

                const response =
                    await fetch(
                        "/api/camera-grid",
                        {

                            credentials:
                                "same-origin"

                        }
                    );


                if(!response.ok){

                    throw new Error(
                        "Camera API unavailable"
                    );

                }


                const data =
                    await response.json();


                const cameras =
                    Array.isArray(
                        data.cameras
                    )
                    ?
                    data.cameras
                    :
                    [];


                cameraGrid.innerHTML =
                    "";


                cameras.forEach(
                    camera => {

                        cameraGrid.appendChild(
                            createCameraCard(
                                camera
                            )
                        );

                    }
                );


                const online =
                    cameras.filter(
                        camera =>
                            camera.status
                            ===
                            "ONLINE"
                    )
                    .length;


                const total =
                    cameras.length;

                const firstOnlineCamera =
                    cameras.find(
                        camera =>
                            camera.status
                            ===
                            "ONLINE"
                    );


                if(firstOnlineCamera){

                    vehicleCameraName =
                        firstOnlineCamera.name;

                }

                else if(
                    cameras.length > 0
                ){

                    vehicleCameraName =
                        cameras[0].name;

                }


                if(cameraOnlineCount){

                    cameraOnlineCount.textContent =
                        online;

                }


                if(topbarCameraCount){

                    topbarCameraCount.textContent =
                        `${online} / ${total}`;

                }


                if(systemCameras){

                    systemCameras.textContent =
                        `${online} / ${total}`;

                }


                if(cameraIndicator){

                    cameraIndicator.classList.toggle(
                        "online",
                        online > 0
                    );


                    cameraIndicator.classList.toggle(
                        "warning",
                        online === 0
                    );

                }


                if(total === 0){

                    cameraGrid.innerHTML =

                        '<div class="grid-loading">'
                        +
                        'Aucune caméra configurée.'
                        +
                        '</div>';

                }

            }

            catch(error){

                console.error(
                    "Phoenix Camera Grid:",
                    error
                );


                cameraGrid.innerHTML =

                    '<div class="grid-loading">'
                    +
                    'Impossible de charger les caméras.'
                    +
                    '</div>';

            }

        }



        /*
        ====================================================
        DASHBOARD SUMMARY
        ====================================================
        */


        function renderEvents(
            events
        ){

            if(
                !eventsList
                ||
                !eventsCount
            ){

                return;

            }


            if(
                !Array.isArray(
                    events
                )
                ||
                events.length === 0
            ){

                eventsCount.textContent =
                    "0";


                eventsList.innerHTML = `

    <div class="events-preview-label">
        APERÇU INTERFACE
    </div>


    <div class="event-item danger">

        <div class="event-title">
            Véhicule suspect
        </div>

        <div class="event-meta">
            <span>CAM03</span>
            <span>--:--</span>
        </div>

    </div>


    <div class="event-item warning">

        <div class="event-title">
            Excès de vitesse
        </div>

        <div class="event-meta">
            <span>CAM01</span>
            <span>--:--</span>
        </div>

    </div>


    <div class="event-item">

        <div class="event-title">
            Plaque non reconnue
        </div>

        <div class="event-meta">
            <span>CAM06</span>
            <span>--:--</span>
        </div>

    </div>


    <div class="event-item danger">

        <div class="event-title">
            Intrusion zone protégée
        </div>

        <div class="event-meta">
            <span>CAM08</span>
            <span>--:--</span>
        </div>

    </div>


    <div class="events-empty compact">

        <span>
            Données d'exemple pour validation visuelle.
        </span>

    </div>

`;


                return;

            }


            eventsCount.textContent =
                events.length;


            eventsList.innerHTML =
                "";


            events.forEach(
                event => {

                    const item =
                        document.createElement(
                            "div"
                        );


                    const severity =
                        event.severity
                        ||
                        "normal";


                    item.className =
                        `event-item ${severity}`;


                    const title =
                        document.createElement(
                            "div"
                        );


                    title.className =
                        "event-title";


                    title.textContent =
                        event.title
                        ||
                        "Événement";


                    const meta =
                        document.createElement(
                            "div"
                        );


                    meta.className =
                        "event-meta";


                    const camera =
                        document.createElement(
                            "span"
                        );


                    camera.textContent =
                        event.camera
                        ||
                        "SYSTEM";


                    const time =
                        document.createElement(
                            "span"
                        );


                    time.textContent =
                        event.time
                        ||
                        "--:--";


                    meta.appendChild(
                        camera
                    );


                    meta.appendChild(
                        time
                    );


                    item.appendChild(
                        title
                    );


                    item.appendChild(
                        meta
                    );


                    eventsList.appendChild(
                        item
                    );

                }
            );

        }



        async function loadDashboardSummary(){

            try{

                const response =
                    await fetch(
                        "/api/dashboard/summary",
                        {

                            credentials:
                                "same-origin"

                        }
                    );


                if(!response.ok){

                    return;

                }


                const data =
                    await response.json();


                renderEvents(
                    data.recent_events
                    ||
                    []
                );


                const system =
                    data.system
                    ||
                    {};


                const ai =
                    document.getElementById(
                        "system-ai"
                    );


                const database =
                    document.getElementById(
                        "system-database"
                    );


                const anpr =
                    document.getElementById(
                        "system-anpr"
                    );


                if(ai){

                    ai.textContent =
                        system.ai_engine
                        ||
                        "En attente";

                }


                if(database){

                    database.textContent =
                        system.database
                        ||
                        "Local";

                }


                if(anpr){

                    anpr.textContent =
                        system.anpr_server
                        ||
                        "En attente";

                }

            }

            catch(error){

                console.error(
                    "Phoenix Dashboard Summary:",
                    error
                );

            }

        }



        /*
        ====================================================
        PLEIN ÉCRAN
        ====================================================
        */


        if(fullscreenButton){

            fullscreenButton.addEventListener(
                "click",
                async () => {

                    try{

                        if(
                            !document.fullscreenElement
                        ){

                            await document
                                .documentElement
                                .requestFullscreen();

                        }

                        else{

                            await document
                                .exitFullscreen();

                        }

                    }

                    catch(error){

                        console.error(
                            "Phoenix Fullscreen:",
                            error
                        );

                    }

                }
            );

        }

        /*
====================================================
VÉHICULE ACTIF
====================================================
*/


function resetVehiclePanel(
    statusText="ATTENTE"
){

    if(vehiclePlate){

        vehiclePlate.textContent =
            "—";

    }


    if(vehicleType){

        vehicleType.textContent =
            "Aucun véhicule actif";

    }


    if(vehicleConfidence){

        vehicleConfidence.textContent =
            "Détection en attente";

    }


    if(vehicleTrackerId){

        vehicleTrackerId.textContent =
            "—";

    }


    if(vehicleZone){

        vehicleZone.textContent =
            "—";

    }


    if(vehicleSpeed){

        vehicleSpeed.textContent =
            "—";

    }


    if(vehicleDirection){

        vehicleDirection.textContent =
            "—";

    }


    if(vehicleThreat){

        vehicleThreat.textContent =
            "—";

    }


    if(vehiclePanelStatus){

        vehiclePanelStatus.textContent =
            statusText;


        vehiclePanelStatus.className =
            "panel-status neutral";

    }

}



async function loadCurrentVehicle(){

    try{

        const response =
            await fetch(

                "/api/current-vehicle/"
                +
                encodeURIComponent(
                    vehicleCameraName
                ),

                {

                    credentials:
                        "same-origin"

                }

            );


        if(!response.ok){

            resetVehiclePanel(
                "ERREUR"
            );

            return;

        }


        const vehicle =
            await response.json();


        if(
            !vehicle.available
        ){

            if(
                vehicle.status
                ===
                "ENGINE_OFF"
            ){

                resetVehiclePanel(
                    "MOTEUR OFF"
                );

            }

            else{

                resetVehiclePanel(
                    "ATTENTE"
                );

            }


            return;

        }


        /*
        ================================================
        PLAQUE
        ================================================
        */


        if(vehiclePlate){

            vehiclePlate.textContent =
                vehicle.plate
                ||
                "Non détectée";

        }


        /*
        ================================================
        TYPE
        ================================================
        */


        if(vehicleType){

            vehicleType.textContent =
                vehicle.type
                ||
                "Véhicule";

        }


        /*
        ================================================
        CONFIANCE
        ================================================
        */


        if(vehicleConfidence){

            const detectionConfidence =
                Number(
                    vehicle.confidence
                    ||
                    0
                )
                .toFixed(1);


            const anprConfidence =
                Number(
                    vehicle.plate_confidence
                    ||
                    0
                )
                .toFixed(1);


            const anprStatus =
                vehicle.plate_status
                ||
                "NOT_DETECTED";


            if(
                vehicle.plate
                &&
                vehicle.plate
                !==
                "Non détectée"
            ){

                vehicleConfidence.textContent =

                    `IA ${detectionConfidence}%`
                    +
                    ` • ANPR ${anprConfidence}%`
                    +
                    ` • ${anprStatus}`;

            }

            else{

                vehicleConfidence.textContent =

                    `IA ${detectionConfidence}%`
                    +
                    ` • ANPR ${anprStatus}`;

            }

        }


        /*
        ================================================
        TRACKER
        ================================================
        */


        if(vehicleTrackerId){

            vehicleTrackerId.textContent =
                vehicle.id
                ??
                "—";

        }


        /*
        ================================================
        ZONE
        ================================================
        */


        if(vehicleZone){

            vehicleZone.textContent =
                vehicle.zone
                ||
                "Aucune";

        }


        /*
        ================================================
        VITESSE
        ================================================
        */


        if(vehicleSpeed){

            vehicleSpeed.textContent =

                Number(
                    vehicle.speed
                    ||
                    0
                )
                .toFixed(1)
                +
                " km/h";

        }


        /*
        ================================================
        DIRECTION
        ================================================
        */


        if(vehicleDirection){

            vehicleDirection.textContent =
                vehicle.direction
                ||
                "Inconnue";

        }


        /*
        ================================================
        MENACE
        ================================================
        */


        if(vehicleThreat){

            vehicleThreat.textContent =
                vehicle.threat
                ||
                "NORMAL";

        }


        /*
        ================================================
        STATUT
        ================================================
        */


        if(vehiclePanelStatus){

            vehiclePanelStatus.textContent =
                "ACTIF";


            const threat =
                String(
                    vehicle.threat
                    ||
                    ""
                )
                .toUpperCase();


            const dangerous = [

                "HIGH",

                "CRITICAL",

                "DANGER",

                "ALERT"

            ]
            .includes(
                threat
            );


            vehiclePanelStatus.className =
                dangerous
                ?
                "panel-status vehicle-alert-status"
                :
                "panel-status vehicle-active-status";

        }

    }

    catch(error){

        console.error(
            "Phoenix Current Vehicle:",
            error
        );


        resetVehiclePanel(
            "ERREUR"
        );

    }

}



        /*
        ====================================================
        DÉMARRAGE
        ====================================================
        */


        loadCurrentUser();


        updateClock();


        window.setInterval(
            updateClock,
            1000
        );


        loadCameras();


        loadDashboardSummary();

        loadCurrentVehicle();


        window.setInterval(
            loadCurrentVehicle,
            3000
        );

    }
);
