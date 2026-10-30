import threading

from flask import Flask, jsonify

from orchid import VanillaOrchid
from power_manager import PowerManager
from peripherals import (
    TemperatureController,
    HumidityController,
    LightController,
    SoilController,
    FungiMonitor,
    CO2Controller,
)

app = Flask(__name__)


class HubState:
    DORMANT = "DORMANT"
    ACTIVE = "ACTIVE"
    FAULT = "FAULT"


class GardenHub:
    def __init__(self):
        self._lock = threading.Lock()
        self._init_state()

    def _init_state(self):
        self.orchid = VanillaOrchid()
        self.power_manager = PowerManager(capacity=1000.0)
        self.controllers = {
            "tc": TemperatureController(),
            "hc": HumidityController(),
            "lc": LightController(),
            "sc": SoilController(),
            "fm": FungiMonitor(),
            "co2": CO2Controller(),
        }
        self._state = HubState.DORMANT
        self._cycle = 0
        self._connect_all()

    def _connect_all(self):
        for ctrl in self.controllers.values():
            ctrl.connect()
        self._state = HubState.ACTIVE

    def reset(self):
        """Restore the hub to its initial state. Primarily used between tests."""
        with self._lock:
            self._init_state()

    def advance_cycle(self):
        """Advance the simulation one cycle: update all peripherals and check orchid health."""
        with self._lock:
            if self._state == HubState.FAULT:
                return

            self._cycle += 1

            tc = self.controllers["tc"]
            hc = self.controllers["hc"]
            lc = self.controllers["lc"]
            sc = self.controllers["sc"]
            fm = self.controllers["fm"]
            co2 = self.controllers["co2"]

            tc.update(power_manager=self.power_manager)
            hc.update(power_manager=self.power_manager)
            lc.update(power_manager=self.power_manager)
            sc.update(power_manager=self.power_manager)
            co2.update(power_manager=self.power_manager)
            fm.update(temperature=tc.temperature, orchid=self.orchid)

            self.orchid.daily_check(tc.temperature)

            if self.power_manager.is_depleted() or not self.orchid.alive:
                self._state = HubState.FAULT

    @property
    def state(self):
        return self._state

    @property
    def cycle(self):
        return self._cycle

    def get_telemetry(self):
        signals = {}
        for ctrl in self.controllers.values():
            signals.update(ctrl.get_telemetry())
        return {"cycle": self._cycle, "signals": signals}


hub = GardenHub()


# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@app.route("/status")
def get_status():
    return jsonify({
        "state": hub.state,
        "orchid_alive": hub.orchid.alive,
        "battery_remaining_pct": round(hub.power_manager.remaining_pct(), 2),
        "cycle": hub.cycle,
    })


@app.route("/controllers")
def list_controllers():
    return jsonify([ctrl.to_dict() for ctrl in hub.controllers.values()])


@app.route("/controllers/<name>")
def get_controller(name):
    ctrl = hub.controllers.get(name)
    if ctrl is None:
        return jsonify({"error": f"Controller '{name}' not found"}), 404
    return jsonify(ctrl.to_dict())


@app.route("/controllers/<name>/version")
def get_controller_version(name):
    ctrl = hub.controllers.get(name)
    if ctrl is None:
        return jsonify({"error": f"Controller '{name}' not found"}), 404
    return jsonify({"name": name, "version": ctrl.get_version()})


@app.route("/telemetry")
def get_telemetry():
    return jsonify(hub.get_telemetry())


@app.route("/orchid")
def get_orchid():
    return jsonify({"alive": hub.orchid.alive})


@app.route("/cycle", methods=["POST"])
def advance_cycle():
    hub.advance_cycle()
    return jsonify({"cycle": hub.cycle, "state": hub.state})


@app.route("/reset", methods=["POST"])
def reset():
    """Reset the hub to its initial state. Intended for use between tests."""
    hub.reset()
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(port=5000, debug=False)
