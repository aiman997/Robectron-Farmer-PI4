import time
from w1thermsensor import W1ThermSensor
from sensors.sensors_interface import SensorInterface
from relays.relay_control import RelayControl

class DS18B20Sensor(SensorInterface):
    def __init__(self, power_relay_pin, max_retries=5, delay=2):
        # Initialize the sensor and relay for power control
        self.sensor = W1ThermSensor()
        self.power_relay = RelayControl(pin=power_relay_pin)  # Relay for power control
        self.status = "Initialized"
        self.max_retries = max_retries  # Max number of retries if reading fails
        self.delay = delay  # Delay between retries

    def power_on(self):
        """Turn on the relay to provide power to the sensor."""
        self.power_relay.activate()
        self.status = "Powered On"

    def power_off(self):
        """Turn off the relay to cut power to the sensor."""
        self.power_relay.deactivate()
        self.status = "Powered Off"

    def read_value(self):
        """Read temperature value from DS18B20 sensor with retries."""
        self.power_on()  # Ensure the sensor is powered on
        self.status = "Reading"

        for attempt in range(self.max_retries):
            try:
                temperature = self.sensor.get_temperature()
                if temperature is not None and temperature > 0.0:
                    self.status = "OK"
                    self.power_off()  # Power off the sensor after reading
                    return {"temperature": temperature}
                else:
                    print(f"Invalid reading on attempt {attempt + 1}. Retrying...")
                    time.sleep(self.delay)  # Wait before retrying
            except RuntimeError as e:
                print(f"Runtime error on attempt {attempt + 1}: {e}")
                time.sleep(self.delay)
            except Exception as e:
                print(f"An error occurred on attempt {attempt + 1}: {e}")
                time.sleep(self.delay)

        self.status = "Error"  # Reading failed after retries
        self.power_off()  # Power off the sensor
        return {"temperature": None}

    def get_status(self):
        """Get the current status of the sensor."""
        return self.status
