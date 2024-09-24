import websockets
import asyncio
import platform
import json
import time
from sensors.DHT22 import DHTSensor
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
        self.retry_delay = 5

        # Dynamically get the board pin from the config file
        dht_data_pin = getattr(board, self.config['dht_sensor_data_pin'])  # e.g., board.D11
        dht_power_pin = self.config['dht_sensor_power_pin']  # e.g., 27

        # Initialize the DHT sensor with the configuration
        self.dht_sensor = DHTSensor(data_pin=dht_data_pin, power_relay_pin=dht_power_pin)

        # Initialize actuators using the configuration
        ec_pump_pin = self.config['ec_pump_pin']  # e.g., 18
        self.relay_actuators = {
            "EC_Pump": RelayControl(pin=ec_pump_pin),
        }

    async def gather_sensor_data(self):
        """Gather data from the DHT sensor."""
        # Get DHT22 sensor data (temperature and humidity)
        sensor_data = self.dht_sensor.read_value()
        sensor_status = self.dht_sensor.get_status()

        # Return the gathered sensor data and status
        return {
            "sensor_data": sensor_data,
            "sensor_status": sensor_status
        }

    async def gather_actuator_status(self):
        """Get the status of all actuators (i.e., relays)."""
        actuator_status = {}
        for name, relay in self.relay_actuators.items():
            actuator_status[name] = relay.get_status()
        return actuator_status

    async def send_data(self, websocket):
        """Send sensor data and actuator status to the backend via WebSocket."""
        # Gather data from DHT sensor
        sensor_info = await self.gather_sensor_data()

        # Gather actuator statuses (e.g., status of EC pump relay)
        actuator_info = await self.gather_actuator_status()

        # Combine sensor data and actuator status into one payload
        payload = {
            "sensor_data": sensor_info["sensor_data"],
            "sensor_status": sensor_info["sensor_status"],
            "actuator_status": actuator_info
        }

        # Send the payload as JSON to the WebSocket server
        await websocket.send(json.dumps(payload))
        print(f"Data sent: {payload}")

    async def handle_commands(self, websocket, command):
        """Handle commands received from the backend."""
        action = command.get("action")
        actuator_name = command.get("actuator")

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

    async def gather_and_send(self):
        """Periodically gather sensor data and actuator status, and send it to the backend."""
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    while True:
                        # Send sensor and actuator data
                        await self.send_data(websocket)
                        await asyncio.sleep(5)  # Wait for 5 seconds before sending again

                        # Listen for commands from the backend
                        await self.listen_and_execute(websocket)
            except (websockets.exceptions.ConnectionClosedError, OSError) as e:
                # If connection fails, log the error and retry after delay
                print(f"Connection error: {e}. Retrying in {self.retry_delay} seconds...")
                await asyncio.sleep(self.retry_delay)

                # Exponential backoff: Increase the retry delay up to a maximum of 60 seconds
                self.retry_delay = min(self.retry_delay * 2, 60)

async def main():
    ws_client = WebSocketClient()
    await ws_client.gather_and_send()

if __name__ == "__main__":
    asyncio.run(main())
