from .base import BasePeripheral


class LightController(BasePeripheral):
    """
    Controls UV grow lights on a 16-hours-on / 8-hours-off daily cycle.
    Switching lights on costs 3 units of power.
    """

    LIGHT_ON_HOURS = 16

    def __init__(self):
        super().__init__("lc", "1.0.4")
        self._total_cycles = 0
        self._light_on = False

    def update(self, power_manager=None):
        self.heartbeat_counter += 1
        self._total_cycles += 1

        hour_of_day = self._total_cycles % 24
        should_be_on = hour_of_day < self.LIGHT_ON_HOURS

        if should_be_on and not self._light_on:
            available = power_manager.consume("lc", 3.0) if power_manager else True
            self._light_on = bool(available)
        elif not should_be_on:
            self._light_on = False

    @property
    def light_on(self):
        return self._light_on

    def get_telemetry(self):
        return {
            "lc_heartbeat": self.heartbeat_counter,
            "lc_light_on": int(self._light_on),
            "lc_hour_of_day": self._total_cycles % 24,
        }
