import platform
import time
from sensors.sensors_interface import SensorInterface
from relays.relay_control import RelayControl

# Conditional import for Adafruit board library (only for Raspberry Pi)
if platform.system() == 'Linux':  # Raspberry Pi
    import board
    import adafruit_dht
else:
    # Mock the board library for non-Linux platforms (macOS/Windows)
    class board:
        D11 = "D11"
        # Add any other board pin constants you might use
    class adafruit_dht:
        class DHT22:
            def __init__(self, pin):
                print(f"Mock DHT22 initialized with pin {pin}")
            
            @property
            def temperature(self):
                return 25.0  # Mock temperature value

            @property
            def humidity(self):
                return 60.0  # Mock humidity value


class DHTSensor(SensorInterface):
    def __init__(self, data_pin, power_relay_pin, max_retries=5, delay=2):
        self.sensor = adafruit_dht.DHT22(data_pin)
        self.status = "Initialized"
        # Relay to control power to the sensor
        self.power_relay = RelayControl(power_relay_pin)
        self.max_retries = max_retries  # Maximum number of retries to get a valid reading
        self.delay = delay  # Delay in seconds between retries

    def power_on(self):
        """Turn on the relay to provide power to the sensor."""
        self.power_relay.activate()
        self.status = "Powered On"

    def power_off(self):
        """Turn off the relay to cut power to the sensor."""
        self.power_relay.deactivate()
        self.status = "Powered Off"

    def read_value(self):
        """Read temperature and humidity values from the sensor with retries."""
        self.power_on()  # Ensure the sensor is powered
        self.status = "Reading"  # Update status to indicate reading is in progress

        for attempt in range(self.max_retries):
            try:
                temperature = self.sensor.temperature
                humidity = self.sensor.humidity
                if temperature is not None and humidity is not None and temperature > 0.0 and humidity > 0.0:
                    self.status = "OK"  # Reading successful
                    self.power_off()  # Optionally turn off the sensor after reading
                    return {"temperature": temperature, "humidity": humidity}
                else:
                    print(f"Invalid reading on attempt {attempt + 1}. Retrying...")
                    time.sleep(self.delay)  # Wait before retrying

            except RuntimeError as e:
                print(f"Error reading DHT22: {e}. Retrying in {self.delay} seconds...")
                time.sleep(self.delay)

        self.status = "Error"  # Sensor read failed after retries
        self.power_off()  # Ensure the sensor is turned off
        return {"temperature": None, "humidity": None}
    
    def get_status(self):
        """Get the current status of the sensor."""
        return self.status
