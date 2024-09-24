from w1thermsensor import W1ThermSensor
import time

sensor = W1ThermSensor()

while True:
    try:
        temperature = sensor.get_temperature()
        print(f"Temp: {temperature:.2f} C")

    except RuntimeError as e:
        print(f"Runtime error while reading DS18B20: {e}")

    except Exception as error:
        print(f"An error occured while reading DS18B20: {error}")

    time.sleep(2)
