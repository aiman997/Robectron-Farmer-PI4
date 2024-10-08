import json
import time
import websockets
import asyncio
import platform
from sensors.EC import ECSensor
from sensors.DHT22 import DHTSensor
from sensors.DS18B20 import DS18B20Sensor
from relays.relay_control import RelayControl

# Conditional import for Adafruit board library (only for Raspberry Pi)
if platform.system() == 'Linux':  # Raspberry Pi
    import board
else:
    # Mock the board library for non-Linux platforms (macOS/Windows)
    class board:
        D11 = "D11"
        # Add any other board pin constants you might use

class WebSocketClient:
    def __init__(self, config_file='config.json'):
        # Load the configuration from the config.json file
        with open(config_file, 'r') as config_file:
            self.config = json.load(config_file)

        # Fetch the WebSocket URL from the config file
        self.uri = self.config["websocket_url_pi"]
        self.retry_delay = 10

        # Dynamically get the board pin from the config file
        dht_data_pin = getattr(board, self.config['dht_sensor_data_pin'])  # board.D11
        dht_power_pin = self.config['dht_sensor_power_pin']
        ds18b20_power_pin = self.config['ds18b20_sensor_power_pin']
        ec_power_pin = self.config['ec_sensor_power_pin']


        # Initialize the DHT sensor with the configuration
        self.dht_sensor = DHTSensor(data_pin=dht_data_pin, power_relay_pin=dht_power_pin)

        # Initialize the DS18B20 sensor with power relay pin from the config file
        self.ds18b20_sensor = DS18B20Sensor(power_relay_pin=ds18b20_power_pin)

        # Initialize the EC sensor
        self.ec_sensor = ECSensor(power_relay_pin=ec_power_pin)

        # Initialize actuators using the configuration
        ec_pump_pin = self.config['ec_pump_pin']
        self.relay_actuators = {
            "EC_Pump": RelayControl(pin=ec_pump_pin),
        }

        # Dictionary to map sensor names to their sensor instances
        self.sensors = {
            "DHT22": self.dht_sensor,
            "DS18B20": self.ds18b20_sensor,
            "EC": self.ec_sensor,
        }

    async def gather_data(self, sensor_name=None):
        """
        Gathers data from a specific sensor or all sensors.
        If sensor_name is None or 'all', it gathers data from all sensors.
        Otherwise, it gathers data from the specified sensor.
        """
        if sensor_name is None or sensor_name == "all":
            # Gather data from all sensors
            all_sensor_data = {}
            for sensor_name, sensor_instance in self.sensors.items():
                sensor_data = sensor_instance.read_value()
                sensor_status = sensor_instance.get_status()
                all_sensor_data[sensor_name] = {
                    "sensor_data": sensor_data,
                    "sensor_status": sensor_status
                }
            return all_sensor_data
        else:
            # Gather data from the specified sensor
            sensor_instance = self.sensors.get(sensor_name)
            if sensor_instance:
                sensor_data = sensor_instance.read_value()
                sensor_status = sensor_instance.get_status()
                return {sensor_name: {"sensor_data": sensor_data, "sensor_status": sensor_status}}
            else:
                # Raise an error if the sensor is not recognized
                raise ValueError(f"Unrecognized sensor: {sensor_name}")

    async def gather_actuator_status(self):
        """Get the status of all actuators (i.e., relays)."""
        actuator_status = {}
        for name, relay in self.relay_actuators.items():
            actuator_status[name] = relay.get_status()
        return actuator_status
    
    async def send_data(self, websocket):
        """Send sensor data and actuator status to the backend via WebSocket."""
        # Gather data from all sensors
        sensor_info = await self.gather_data()

        # Gather actuator statuses (e.g., status of EC pump relay)
        actuator_info = await self.gather_actuator_status()

        # Combine sensor data and actuator status into one payload
        payload = {
            "sensor_data": sensor_info,
            "actuator_status": actuator_info
        }

        # Send the payload as JSON to the WebSocket server
        await websocket.send(json.dumps(payload))
        print(f"Data sent: {payload}")

    async def handle_commands(self, websocket, command):
        """Handle commands received from the backend."""
        action = command.get("action")
        actuator_name = command.get("actuator")
        sensor_name = command.get("sensor")

        if action == "activate":
            if actuator_name in self.relay_actuators:
                self.relay_actuators[actuator_name].activate()
                await websocket.send(f"{actuator_name} activated")
                print(f"{actuator_name} activated")

        elif action == "deactivate":
            if actuator_name in self.relay_actuators:
                self.relay_actuators[actuator_name].deactivate()
                await websocket.send(f"{actuator_name} deactivated")
                print(f"{actuator_name} deactivated")

        elif action == "get_reading":
            # Use gather_data to retrieve sensor readings dynamically
            try:
                sensor_info = await self.gather_data(sensor_name)
                await websocket.send(json.dumps({
                    "status": "reading_received",
                    "sensor": sensor_name,
                    "data": sensor_info
                }))
                print(f"{sensor_name} sensor data sent: {sensor_info}")
            except ValueError as e:
                # Handle the case where the sensor is not recognized
                await websocket.send(json.dumps({
                    "status": "error",
                    "message": str(e)
                }))
                print(f"Error: {str(e)}")

        elif action == "get_status":
            # If a status request is received, gather and send data
            await self.send_data(websocket)

    async def listen_and_execute(self, websocket):
        """Main loop to listen for commands from the backend and execute actions."""
        try:
            async for message in websocket:
                if not message.strip():  # Check for empty or whitespace-only message
                    print("Received empty or whitespace message, skipping...")
                    continue

                try:
                    command = json.loads(message)  # Attempt to decode the JSON message
                    print(f"Received command: {command}")
                    await self.handle_commands(websocket, command)
                except json.JSONDecodeError as e:
                    print(f"Failed to decode JSON message: {e}. Received: {message}")
                    error_response = json.dumps({"error": "Invalid JSON", "details": str(e)})
                    await websocket.send(error_response)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")

    async def gather_data_periodically(self, websocket, interval=60):
        """Periodically gather sensor data and send it to the backend."""
        while True:
            await self.send_data(websocket)
            await asyncio.sleep(interval)

    async def gather_and_send(self):
        """Main function to gather and send data periodically and listen for commands."""
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    # Run both gather_data_periodically and listen_for_commands concurrently
                    gather_task = asyncio.create_task(self.gather_data_periodically(websocket, 60))
                    listen_task = asyncio.create_task(self.listen_and_execute(websocket))

                    # Wait for both tasks to run concurrently
                    await asyncio.gather(gather_task, listen_task)

            except (websockets.exceptions.ConnectionClosedError, OSError) as e:
                print(f"Connection error: {e}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)
                self.retry_delay = min(self.retry_delay * 2, 60)

async def main():
    ws_client = WebSocketClient()
    await ws_client.gather_and_send()

if __name__ == "__main__":
    asyncio.run(main())