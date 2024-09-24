# sensors/sensors_interface.py

from abc import ABC, abstractmethod

class SensorInterface(ABC):
    @abstractmethod
    def read_value(self):
        pass

    @abstractmethod
    def get_status(self):
        pass
