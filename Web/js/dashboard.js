// War Galley Admin Dashboard — real-time telemetry via engine_state.json IPC
"use strict";

// Initialise fleet chart with safe default data
const ctx = document.getElementById("fleetChart").getContext("2d");
const fleetChart = new Chart(ctx, {
    type: "doughnut",
    data: {
        labels: ["Active", "Sunk", "Autonomous"],
        datasets: [{
            data: [0, 0, 0],
            backgroundColor: ["#2ecc71", "#e74c3c", "#f1c40f"]
        }]
    },
    options: { responsive: true }
});

/**
 * Fetch telemetry from the API and update all dashboard elements.
 * Called immediately on load and then every 5 seconds.
 */
async function updateDashboard() {
    try {
        const response = await fetch("/api/v1/telemetry", {
            headers: {
                // ADMIN_API_KEY injected at deploy time via a meta tag or env config
                "Authorization": "Bearer " + (window.ADMIN_API_KEY || "")
            }
        });

        if (!response.ok) {
            console.warn("Telemetry request rejected:", response.status);
            document.getElementById("engine-status").innerText = "AUTH ERROR";
            return;
        }

        const data = await response.json();

        // Update status text fields
        document.getElementById("engine-status").innerText =
            data.engine_running ? "ONLINE" : "OFFLINE";

        // Update fleet doughnut chart with live vessel counts
        updateFleetChart(data);

        // Prepend new log entries without duplicating existing ones
        const logContainer = document.getElementById("log-container");
        (data.recent_logs || []).forEach(log => {
            const entry = document.createElement("div");
            entry.innerText = `[${log.timestamp}] ${log.event}: ${log.message}`;
            logContainer.prepend(entry);
        });

    } catch (error) {
        console.error("Critical: Failed to connect to Authoritative Engine.", error);
        document.getElementById("engine-status").innerText = "OFFLINE";
    }
}

/**
 * Update the fleet doughnut chart from the telemetry data object.
 * @param {Object} data - Telemetry response from /api/v1/telemetry
 */
function updateFleetChart(data) {
    const active     = data.active_vessels     || 0;
    const sunk       = data.sunk_vessels       || 0;
    const autonomous = data.autonomous_vessels || 0;

    fleetChart.data.datasets[0].data = [active, sunk, autonomous];
    fleetChart.update();
}

// Call immediately on page load so the dashboard is never blank
updateDashboard();

// Then poll every 5 seconds
setInterval(updateDashboard, 5000);
