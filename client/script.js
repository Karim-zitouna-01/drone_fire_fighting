/* ============================================================
   STREAM SELECTION (left and right video windows)
   ============================================================ */

// Stream A
document.querySelectorAll("input[name='droneA']").forEach(btn => {
    btn.addEventListener("change", () => {
        const id = document.querySelector("input[name='droneA']:checked").value;
        document.getElementById("streamA").src = `http://localhost:8000/video/stream/${id}`;
    });
});

// Stream B
document.querySelectorAll("input[name='droneB']").forEach(btn => {
    btn.addEventListener("change", () => {
        const id = document.querySelector("input[name='droneB']:checked").value;
        document.getElementById("streamB").src = `http://localhost:8000/video/stream/${id}`;
    });
});



/* ============================================================
   WEBSOCKET — RECEIVE HISTORY PACKETS FROM SERVER
   ============================================================ */

console.log("Connecting to WebSocket…");

// Dashboard WebSocket (fixed)
const ws = new WebSocket("ws://localhost:8000/ws/dashboard");


ws.onopen = () => {
    console.log("Dashboard WebSocket connected.");
};

ws.onclose = () => {
    console.log("Dashboard WebSocket disconnected.");
};

ws.onerror = err => {
    console.error("WS error:", err);
};


/* ============================================================
   TABLE: render last 10 entries pushed by WS
   ============================================================ */

const tableBody = document.querySelector("#data-table tbody");

// Clear table
function clearTable() {
    tableBody.innerHTML = "";
}

// Render one history packet (10 new rows)
function renderHistoryPacket(drone_id, history) {
    clearTable();

    history.forEach(entry => {
        const timestamp = new Date(entry.timestamp * 1000).toLocaleString();

        const thumb = entry.image
            ? `<img class="thumbnail-img" src="data:image/jpeg;base64,${entry.image}">`
            : "";

        const gps = `${entry.position?.gps_lat?.toFixed(4)}, ${entry.position?.gps_lon?.toFixed(4)}`;

        const row = `
            <tr>
                <td>${timestamp}</td>
                <td>${drone_id}</td>
                <td>${thumb}</td>
                <td>${entry.danger.danger_score}</td>
                <td>${gps}</td>
                <td>${entry.data_info.real_temp}</td>
                <td>${entry.data_info.real_co2}</td>
                <td>${entry.people_count}</td>
                <td>${entry.img_info.raw_description}</td>
            </tr>
        `;

        tableBody.insertAdjacentHTML("beforeend", row);
    });
}



/* ============================================================
   HANDLE INCOMING WS MESSAGES
   ============================================================ */

ws.onmessage = event => {
    try {
        const packet = JSON.parse(event.data);

        if (packet.type === "history_update") {
            const { drone_id, history } = packet;

            // history is always last 10 entries
            console.log(`Received history update for drone ${drone_id}`);

            renderHistoryPacket(drone_id, history);
        }

    } catch (err) {
        console.error("Invalid WS packet:", err);
    }
};
