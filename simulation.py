"""
Runs a 20-day simulation of the Smart Garden Hub.

Starts the GardenHub REST API server in a background thread, then drives
20 days × 24 cycles through the HTTP API and writes telemetry to telemetry.csv.
"""

import csv
import threading
import time

import requests

from garden_hub import app, hub

BASE_URL = "http://localhost:5000"
DAYS = 20
CYCLES_PER_DAY = 24

CSV_FIELDS = [
    "Cycle",
    "Day",
    "HubState",
    "BatteryRemainingPct",
    "TCTemperature",
    "TCPowerUsed",
    "HCHumidity",
    "HCMistingActive",
    "LCLightOn",
    "SCMoisture",
    "SCpH",
    "FMSporeCount",
    "OrchidAlive",
]


def start_server():
    app.run(port=5000, debug=False, use_reloader=False)


def wait_for_server(timeout=10.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            requests.get(f"{BASE_URL}/status", timeout=0.5)
            return
        except requests.ConnectionError:
            time.sleep(0.1)
    raise RuntimeError("GardenHub server did not start in time.")


if __name__ == "__main__":
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    wait_for_server()

    with open("telemetry.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for day in range(1, DAYS + 1):
            for _ in range(CYCLES_PER_DAY):
                requests.post(f"{BASE_URL}/cycle")

                status = requests.get(f"{BASE_URL}/status").json()
                telem = requests.get(f"{BASE_URL}/telemetry").json()
                signals = telem["signals"]

                writer.writerow({
                    "Cycle": telem["cycle"],
                    "Day": day,
                    "HubState": status["state"],
                    "BatteryRemainingPct": status["battery_remaining_pct"],
                    "TCTemperature": signals.get("tc_temperature"),
                    "TCPowerUsed": signals.get("tc_power_used"),
                    "HCHumidity": signals.get("hc_humidity"),
                    "HCMistingActive": signals.get("hc_misting_active"),
                    "LCLightOn": signals.get("lc_light_on"),
                    "SCMoisture": signals.get("sc_moisture"),
                    "SCpH": signals.get("sc_ph"),
                    "FMSporeCount": signals.get("fm_spore_count"),
                    "OrchidAlive": status["orchid_alive"],
                })

    final = requests.get(f"{BASE_URL}/status").json()
    print(f"Simulation complete after {DAYS} days.")
    print(f"  Hub state   : {final['state']}")
    print(f"  Orchid alive: {final['orchid_alive']}")
    print(f"  Battery left: {final['battery_remaining_pct']:.1f}%")
    print("Telemetry written to telemetry.csv")
