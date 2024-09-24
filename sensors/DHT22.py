import time 
import platform
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
    def __init__(self, data_pin, power_relay_pin):
        self.sensor = adafruit_dht.DHT22(data_pin)
        self.status = "Initialized"
        # Relay to control power to the sensor
        self.power_relay = RelayControl(power_relay_pin)

    def power_on(self):
        """Turn on the relay to provide power to the sensor."""
        self.power_relay.activate()
        self.status = "Powered On"
        # Wait for 5 seconds to allow the sensor to stabilize
        time.sleep(5)

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
