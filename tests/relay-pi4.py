import RPi.GPIO as GPIO
from time import sleep
import atexit

# Pin numbering mode
GPIO.setmode(GPIO.BCM)

# Define labels and pin numbers
labels_m = ['PH', 'EC', 'TP', 'WF', 'LL', 'CUR', 'DCFAN', 'SV', 'HDTY']
labels_p = ['MP', 'DP', 'HDRF', 'LIGHT', 'FAN', 'AIR']
labels_c = ['ECA', 'ECB', 'PHUP', 'PHDN']
#labels_d = ['WFIN', 'LLIN', 'FLIN', 'HIN']
labels = labels_m + labels_p + labels_c

main = [17, 27, 22, 5, 6, 13, 19, 26, 15]
power = [20, 21, 12, 16, 7, 14]
chemist = [18, 23, 24, 25]
#digitin = [9, 8]

# Combine all pins
combined = main + power + chemist

# Create dictionaries for labels and pins
C = {label: value for label, value in zip(labels, combined)}

# Initialize output pins
outputs = {label: C[label] for label in C}
for pin in outputs.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Initial value off

# Initialize input pins
#inputs = {label: pin for label, pin in zip(labels_d, digitin)}
#for pin in inputs.values():
#    GPIO.setup(pin, GPIO.IN)

# Function to turn on devices
def turn_on_devices(device_list):
    for device in device_list:
        pin = C[device]
        GPIO.output(pin, GPIO.HIGH)
        print(f"Device ON: {device}\nPin: {pin}")
        sleep(1)

# Function to turn off devices
def turn_off_devices(device_list):
    for device in device_list:
        pin = C[device]
        GPIO.output(pin, GPIO.LOW)
        print(f"Device OFF\nPin: {pin}")
        sleep(1)

def test_devices(device_list, period):
    for device in device_list:
        pin = C[device]
        GPIO.output(pin, GPIO.HIGH)
        sleep(period)
        GPIO.output(pin, GPIO.LOW)
        sleep(1)
        

# Cleanup function to reset GPIO settings
def cleanup():
    GPIO.cleanup()

try:
    print(C)

    # Turn on main, power, and chemist devices
    #turn_on_devices(labels_m + labels_p)
    #sleep(1)  # Delay for stability

    # Turn off main, power, and chemist devices
    #turn_off_devices(labels_m + labels_p)
    #sleep(1)  # Delay for stability
    turn_on_devices(labels_m + labels_p + labels_c)

    #test_devices(labels_c, 4)

    while True:
        pass

except KeyboardInterrupt:
    print('QUIT')

# Register cleanup function to run at exit
atexit.register(cleanup)

