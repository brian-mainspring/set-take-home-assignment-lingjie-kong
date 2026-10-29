import random

from .base import BasePeripheral
from .sensor_generator import SensorGenerator


class TemperatureController(BasePeripheral):
    """
    Regulates enclosure temperature by heating or cooling one degree per step.
    Each degree of adjustment costs 1 unit of power from the PowerManager.
    """

    TEMP_MIN = 21
    TEMP_MAX = 26
    STEPS_PER_CYCLE = 24

    def __init__(self):
        super().__init__("tc", "2.1.0")
        self._env_temp = SensorGenerator(random.uniform(15.0, 35.0), 0.0, 50.0, 2.0)
        self._temperature = self._env_temp.value
        self._power_used_this_cycle = 0.0

    def update(self, power_manager=None):
        self.heartbeat_counter += 1
        self._power_used_this_cycle = 0.0

        self._temperature = self._env_temp.next()

        for _ in range(self.STEPS_PER_CYCLE):
            if self._temperature > self.TEMP_MAX:
                available = power_manager.consume("tc", 1.0) if power_manager else True
                if available:
                    self._temperature -= 1.0
                    self._power_used_this_cycle += 1.0
                else:
                    break
            elif self._temperature < self.TEMP_MIN:
                available = power_manager.consume("tc", 1.0) if power_manager else True
                if available:
                    self._temperature += 1.0
                    self._power_used_this_cycle += 1.0
                else:
                    break

    @property
    def temperature(self):
        return self._temperature

    def get_telemetry(self):
        return {
            "tc_heartbeat": self.heartbeat_counter,
            "tc_temperature": round(self._temperature, 2),
            "tc_power_used": round(self._power_used_this_cycle, 2),
        }
