import random

from .base import BasePeripheral
from .sensor_generator import SensorGenerator


class CO2Controller(BasePeripheral):
    """
    Monitors CO2 concentration (ppm) inside the enclosure and runs a ventilation
    check each cycle to keep levels within a safe range.

    TODO (Bonus C): Implement this class following the pattern of the other
    peripheral controllers.

    Requirements:
    - CO2 levels should follow a random walk in the range 400–2000 ppm.
      Use the SensorGenerator instance (_co2_gen) already wired up below,
      following the same pattern as TemperatureController and HumidityController.
    - Each cycle, consume 0.5 power units from the PowerManager for the
      ventilation check. If power is unavailable, skip the check.
    - Emit the following telemetry signals each cycle:
        "co2_heartbeat"  — heartbeat counter (int)
        "co2_ppm"        — current CO2 level in ppm (float, rounded to 1 decimal)
    - Register this controller with the GardenHub under the code "co2".
      You will need to update peripherals/__init__.py and garden_hub.py.
    """

    CO2_MIN = 400.0
    CO2_MAX = 2000.0

    def __init__(self):
        super().__init__("co2", "1.0.0")
        self._co2_gen = SensorGenerator(random.uniform(600.0, 1000.0), self.CO2_MIN, self.CO2_MAX, 50.0)
        self._co2_ppm = self._co2_gen.value

    def update(self, power_manager=None):  
        self.heartbeat_counter += 1        
        available = power_manager.consume("co2", 0.5)
        if available:
            self._co2_ppm = self._co2_gen.next()
                
    def get_telemetry(self):
        return {
            "co2_heartbeat": self.heartbeat_counter,
            "co2_ppm": round(self._co2_ppm, 1),
        }
