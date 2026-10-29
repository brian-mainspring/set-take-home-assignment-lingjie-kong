import random

from .base import BasePeripheral
from .sensor_generator import SensorGenerator


class SoilController(BasePeripheral):
    """
    Read-only sensor that reports soil moisture and pH.
    Does not actuate and consumes no power.
    """

    def __init__(self):
        super().__init__("sc", "1.1.1")
        self._moisture_gen = SensorGenerator(random.uniform(0.4, 0.8), 0.0, 1.0, 0.05)
        self._ph_gen = SensorGenerator(random.uniform(5.5, 7.5), 4.0, 9.0, 0.1)
        self._moisture = self._moisture_gen.value
        self._ph = self._ph_gen.value

    def update(self, power_manager=None):
        self.heartbeat_counter += 1

        self._moisture = self._moisture_gen.next()
        self._ph = self._ph_gen.next()

    @property
    def moisture(self):
        return self._moisture

    @property
    def ph(self):
        return self._ph

    def get_telemetry(self):
        return {
            "sc_heartbeat": self.heartbeat_counter,
            "sc_moisture": round(self._moisture, 3),
            "sc_ph": round(self._ph, 2),
        }
