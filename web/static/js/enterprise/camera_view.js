/*
========================================================
PHOENIX VISION AI

Enterprise Camera View

Phoenix Security Technologies
========================================================
*/


async function refreshVehicle(){


    try {


        const response = await fetch(

            "/api/current-vehicle/" + CAMERA

        );


        const vehicle = await response.json();


        const panel = document.getElementById(

            "vehicle-info"

        );


        panel.innerHTML = `


        <div class="info-item">

            <span>ID TRACKER</span>

            <b>${vehicle.id}</b>

        </div>


        <div class="info-item">

            <span>TYPE</span>

            <b>${vehicle.type}</b>

        </div>


        <div class="info-item">

            <span>PLAQUE</span>

            <b>${vehicle.plate}</b>

        </div>


        <div class="info-item">

            <span>CONFIANCE IA</span>

            <b>${vehicle.confidence}%</b>

        </div>


        <div class="info-item">

            <span>ZONE</span>

            <b>${vehicle.zone}</b>

        </div>


        <div class="info-item">

            <span>VITESSE</span>

            <b>${vehicle.speed}</b>

        </div>


        <div class="info-item">

            <span>DIRECTION</span>

            <b>${vehicle.direction}</b>

        </div>


        <div class="info-item threat-${vehicle.threat.toLowerCase()}">

            <span>NIVEAU MENACE</span>

            <b>${vehicle.threat}</b>

        </div>


        <div class="info-item">

            <span>STATUT</span>

            <b>${vehicle.status}</b>

        </div>


        `;


    }


    catch(error){


        console.error(

            "Erreur véhicule:",

            error

        );


    }


}



setInterval(

    refreshVehicle,

    1000

);


refreshVehicle();