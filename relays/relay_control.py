# relays/relay_control.py
import RPi.GPIO as GPIO

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
