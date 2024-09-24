import adafruit_dht
import board
from sensors.sensors_interface import SensorInterface
from relays.relay_control import RelayControl


class DHTSensor(SensorInterface):
    def __init__(self, data_pin, power_relay_pin):
        self.sensor = adafruit_dht.DHT22(data_pin)
        self.status = "Initialized"
        # Relay to control power to the sensor
        self.power_relay = RelayControl(power_relay_pin)

    def power_on(self):
        """Turn on the relay to provide power to the sensor."""
        self.power_relay.activate()
        self.status = "Powered On"

    def power_off(self):
        """Turn off the relay to cut power to the sensor."""
        self.power_relay.deactivate()
        self.status = "Powered Off"

    def read_value(self):
        """Read temperature and humidity values from the sensor."""
        self.power_on()  # Ensure the sensor is powered
        self.status = "Reading"  # Update status to indicate reading is in progress
        try:
            temperature = self.sensor.temperature
            humidity = self.sensor.humidity
            if temperature is not None and humidity is not None:
                self.power_off()  # Optionally turn off the sensor after reading
                self.status = "OK"  # Reading successful
                return {"temperature": temperature, "humidity": humidity}
            else:
                self.status = "Error"  # Sensor read failed
                return {"temperature": None, "humidity": None}
        except RuntimeError as e:
            print(f"Error reading DHT22: {e}")
            self.status = "Error"  # In case of an exception, set the status to Error
            return {"temperature": None, "humidity": None}
    
    def get_status(self):
        """Get the current status of the sensor."""
        return self.status
