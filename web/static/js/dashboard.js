// ----------------------
// HORLOGE
// ----------------------

function updateClock() {
    const now = new Date();
    const clock = document.getElementById("clock");

    if (clock) {
        clock.innerText = now.toLocaleTimeString();
    }
}

updateClock();
setInterval(updateClock, 1000);


// ----------------------
// VEHICLE PANEL
// ----------------------

const panel = document.getElementById("vehicle-panel");
const close = document.getElementById("close-panel");

if (close) {

    close.onclick = () => {

        panel.classList.add("hidden");

    };

}


// ----------------------
// CAMERA GRID
// ----------------------

async function loadCameraGrid() {

    const response = await fetch("/api/camera-grid");

    const data = await response.json();

    const grid = document.getElementById("camera-grid");

    grid.innerHTML = "";

    data.cameras.forEach(camera => {

        const card = document.createElement("div");

        card.className = "camera-card";

        card.innerHTML = `
            <div class="camera-header">
                <span>${camera.name}</span>
                <span class="${camera.status === "ONLINE" ? "online" : "offline"}">
                    ${camera.status}
                </span>
            </div>

            <div class="camera-preview">

            <img
            src="/video/${camera.name}"
            class="camera-stream">

            </div>

            <div class="camera-footer">
                ${camera.location}
            </div>
        `;

        card.onclick = () => {

            if (panel) {
                panel.classList.remove("hidden");
            }

        };

        grid.appendChild(card);

    });

}

loadCameraGrid();