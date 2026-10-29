from abc import ABC, abstractmethod


class BasePeripheral(ABC):
    def __init__(self, name, firmware_version):
        self.name = name
        self.firmware_version = firmware_version
        self.connected = False
        self.heartbeat_counter = 0
        self._status = "INIT"

    def connect(self):
        self.connected = True
        self._status = "RUNNING"

    def get_version(self):
        if not self.connected:
            return "UNKNOWN"
        return self.firmware_version

    @abstractmethod
    def update(self, **kwargs):
        """Advance the peripheral one simulation cycle."""

    @abstractmethod
    def get_telemetry(self):
        """Return a dict of telemetry signal names → values for this cycle."""

    def to_dict(self):
        return {
            "name": self.name,
            "connected": self.connected,
            "firmware_version": self.get_version(),
            "status": self._status,
        }
