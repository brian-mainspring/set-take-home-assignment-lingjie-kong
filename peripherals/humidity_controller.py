import random

from .base import BasePeripheral
from .sensor_generator import SensorGenerator


class HumidityController(BasePeripheral):
    """
    Maintains relative humidity within the optimal range for vanilla orchids.
    Misting costs 2 units of power; ventilation costs 1 unit.
    """

    HUMIDITY_MIN = 50.0
    HUMIDITY_MAX = 70.0

    def __init__(self):
        super().__init__("hc", "1.3.0")
        self._env_humidity = SensorGenerator(random.uniform(40.0, 80.0), 0.0, 100.0, 3.0)
        self._humidity = self._env_humidity.value
        self._misting_active = False

    def update(self, power_manager=None):
        self.heartbeat_counter += 1
        self._misting_active = False

        self._humidity = self._env_humidity.next()

        if self._humidity < self.HUMIDITY_MIN:
            available = power_manager.consume("hc", 2.0) if power_manager else True
            if available:
                self._humidity += 5.0
                self._misting_active = True
        elif self._humidity > self.HUMIDITY_MAX:
            available = power_manager.consume("hc", 1.0) if power_manager else True
            if available:
                self._humidity -= 3.0

    @property
    def humidity(self):
        return self._humidity

    def get_telemetry(self):
        return {
            "hc_heartbeat": self.heartbeat_counter,
            "hc_humidity": round(self._humidity, 2),
            "hc_misting_active": int(self._misting_active),
        }
