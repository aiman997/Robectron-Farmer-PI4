# relays/relay_control.py
import platform

# Conditional import: Use RPi.GPIO only if running on Raspberry Pi
if platform.system() == 'Linux':  # Likely to be a Raspberry Pi
    import RPi.GPIO as GPIO
else:
    # Mock GPIO class for non-Raspberry Pi systems (like macOS or Windows)
    class GPIO:
        BCM = "BCM"
        OUT = "OUT"
        LOW = "LOW"
        HIGH = "HIGH"

        @staticmethod
        def setmode(mode):
            print(f"Set mode to: {mode}")

        @staticmethod
        def setup(pin, mode):
            print(f"Setup pin {pin} with mode {mode}")

        @staticmethod
        def output(pin, state):
            print(f"Set pin {pin} to state {state}")

        @staticmethod
        def cleanup(pin=None):
            print(f"Cleanup pin {pin}")


class RelayControl:
    def __init__(self, pin):
        """Initialize the relay with the specified GPIO pin."""
        self.pin = pin
        self.status = "OFF"  # Initial status of the relay is OFF
        
        # Set up GPIO mode and configure the relay pin as an output
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, GPIO.LOW)  # Ensure the relay starts in the OFF state

    def activate(self):
        """Turn on the relay (activate the device)."""
        GPIO.output(self.pin, GPIO.HIGH)
        self.status = "ON"
        print(f"Relay on pin {self.pin} activated (ON)")

    def deactivate(self):
        """Turn off the relay (deactivate the device)."""
        GPIO.output(self.pin, GPIO.LOW)
        self.status = "OFF"
        print(f"Relay on pin {self.pin} deactivated (OFF)")

    def get_status(self):
        """Get the current status of the relay (ON or OFF)."""
        return self.status

    def cleanup(self):
        """Clean up GPIO settings."""
        GPIO.cleanup(self.pin)
        print(f"Cleaned up GPIO pin {self.pin}")
