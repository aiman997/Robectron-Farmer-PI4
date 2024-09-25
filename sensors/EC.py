import platform
import time
from sensors.sensors_interface import SensorInterface
from relays.relay_control import RelayControl

# Import the necessary EC sensor dependencies from the libs directory
if platform.system() == 'Linux':  # Only import these on Linux (Raspberry Pi)
    from libs.ADS1115 import ADS1115
    from libs.DF_EC import DFRobot_EC
else:
    # Mock the EC sensor behavior for non-Linux platforms
    class ADS1115:
        def setAddr_ADS1115(self, addr):
            print(f"Mock set ADC address to {addr}")

        def setGain(self, gain):
            print(f"Mock set ADC gain to {gain}")

        def readVoltage(self, channel):
            return {"r": 1.23}  # Mock ADC voltage reading

    class DFRobot_EC:
        def begin(self):
            print("Mock EC sensor initialized")

        def readEC(self, voltage, temperature):
            return voltage * 0.5  # Mock EC value calculation

class ECSensor(SensorInterface):
    def __init__(self, power_relay_pin, adc_address=0x48, gain=0x00, max_retries=5, delay=2):
        self.ads1115 = ADS1115()  # Initialize ADC for the EC sensor
        self.ec = DFRobot_EC()    # Initialize EC measurement class
        self.status = "Initialized"
        self.power_relay = RelayControl(power_relay_pin)
        self.adc_address = adc_address
        self.gain = gain
        self.max_retries = max_retries
        self.delay = delay
        
        # Start EC sensor calibration or setup
        self.power_on()  # Ensure the sensor is powered before starting calibration/setup
        self.ec.begin()
        self.power_off()  # Optionally power off after initialization

    def power_on(self):
        """Turn on the relay to provide power to the sensor."""
        self.power_relay.activate()
        self.status = "Powered On"

    def power_off(self):
        """Turn off the relay to cut power to the sensor."""
        self.power_relay.deactivate()
        self.status = "Powered Off"

    def read_value(self, temperature=25):
        """Read EC sensor values with retries."""
        self.power_on()  # Ensure the sensor is powered before reading
        self.status = "Reading"

        for attempt in range(self.max_retries):
            try:
                # Set ADC address and gain for the ADS1115
                self.ads1115.setAddr_ADS1115(self.adc_address)
                self.ads1115.setGain(self.gain)

                # Read the EC value from the ADC and convert it
                adc0 = self.ads1115.readVoltage(0)
                ec_value = self.ec.readEC(adc0['r'], temperature)

                if ec_value is not None and ec_value > 0:
                    self.status = "OK"
                    self.power_off()  # Power off after successful reading
                    return {"ec_value": ec_value, "temperature": temperature}
                else:
                    print(f"Invalid EC reading on attempt {attempt + 1}. Retrying...")
                    time.sleep(self.delay)

            except RuntimeError as e:
                print(f"Error reading EC sensor: {e}. Retrying in {self.delay} seconds...")
                time.sleep(self.delay)

        self.status = "Error"
        self.power_off()  # Ensure power is off even after failed attempts
        return {"ec_value": None, "temperature": None}

    def get_status(self):
        """Get the current status of the EC sensor."""
        return self.status
