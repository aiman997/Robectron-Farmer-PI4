# actuators/actuators_interface.py

from abc import ABC, abstractmethod

class ActuatorInterface(ABC):
    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass
