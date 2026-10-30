from .base import BasePeripheral

LETHAL_SPORE_COUNT = 512


class FungiMonitor(BasePeripheral):
    """
    Passive monitor that tracks fungal spore growth inside the enclosure.
    Does not actuate and consumes no power.
    """

    GROWTH_TEMP_MIN = 25
    GROWTH_TEMP_MAX = 26

    def __init__(self):
        super().__init__("fm", "1.0.0")
        self._spore_count = 1

    def update(self, temperature, orchid=None):
        """
        Advance the fungi monitor one cycle.

        Args:
            temperature: current enclosure temperature from the TemperatureController.
            orchid: the VanillaOrchid instance shared with the GardenHub.
        """
        self.heartbeat_counter += 1
        
        # TODO: Implement fungal growth logic using the constants defined above.
        # Spores double each cycle within the growth temperature range; kill the orchid at LETHAL_SPORE_COUNT.
        if self.GROWTH_TEMP_MIN <= temperature <= self.GROWTH_TEMP_MAX:
            self._spore_count *= 2 
        
        if orchid and self._spore_count >= LETHAL_SPORE_COUNT:
            orchid.kill()

    @property
    def spore_count(self):
        return self._spore_count

    def get_telemetry(self):
        return {
            "fm_heartbeat": self.heartbeat_counter,
            "fm_spore_count": self._spore_count,
        }
