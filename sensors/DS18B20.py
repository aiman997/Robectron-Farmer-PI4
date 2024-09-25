import platform
import time
from sensors.sensors_interface import SensorInterface
from relays.relay_control import RelayControl

# Conditional import for w1thermsensor (only for Raspberry Pi)
if platform.system() == 'Linux':  # Raspberry Pi
    from w1thermsensor import W1ThermSensor, NoSensorFoundError
else:
    # Mock the W1ThermSensor class for non-Linux platforms (macOS/Windows)
    class W1ThermSensor:
        def __init__(self):
            print("Mock DS18B20 sensor initialized.")
        
        def get_temperature(self):
            return 22.5  # Mock temperature value
    
    class NoSensorFoundError(Exception):
        pass


class DS18B20Sensor(SensorInterface):
    def __init__(self, power_relay_pin, max_retries=5, delay=2):
        # Initialize the relay for power control
        self.power_relay = RelayControl(pin=power_relay_pin)
        self.status = "Initialized"
        self.max_retries = max_retries  # Max number of retries if reading fails
        self.delay = delay  # Delay between retries
        self.sensor = None

    def power_on(self):
        """Turn on the relay to provide power to the sensor."""
        self.power_relay.activate()
        self.status = "Powered On"

    def power_off(self):
        """Turn off the relay to cut power to the sensor."""
        self.power_relay.deactivate()
        self.status = "Powered Off"

    def initialize_sensor(self):
        """Initialize the DS18B20 sensor after powering it on."""
        try:
            self.sensor = W1ThermSensor()  # This is either the real or mock sensor
            self.status = "Initialized"
            return True
        except NoSensorFoundError:
            print("Could not find DS18B20 sensor. Retrying...")
            self.status = "Initialization Failed"
            return False

    def read_value(self):
        """Read temperature value from DS18B20 sensor with retries."""
        self.power_on()  # Ensure the sensor is powered on
        self.status = "Reading"

        for attempt in range(self.max_retries):
            try:
                # Ensure sensor is initialized before reading
                if self.sensor is None or self.status == "Initialization Failed":
                    if not self.initialize_sensor():
                        print(f"Retrying initialization... Attempt {attempt + 1}/{self.max_retries}")
                        time.sleep(self.delay)
                        continue

                temperature = self.sensor.get_temperature()
                if temperature is not None:
                    self.status = "OK"
                    self.power_off()  # Optionally turn off the sensor after reading
                    return {"temperature": temperature}
                else:
                    print(f"Invalid reading on attempt {attempt + 1}. Retrying...")
                    time.sleep(self.delay)  # Wait before retrying
            except NoSensorFoundError as e:
                print(f"Error reading DS18B20: {e}. Retrying in {self.delay} seconds...")
                time.sleep(self.delay)
            except Exception as e:
                print(f"An error occurred while reading DS18B20: {e}. Retrying...")
                time.sleep(self.delay)

        self.status = "Error"  # Reading failed after retries
        self.power_off()  # Ensure the sensor is turned off
        return {"temperature": None}

    def get_status(self):
        """Get the current status of the sensor."""
        return self.status
