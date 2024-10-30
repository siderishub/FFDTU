from flask import Flask, render_template
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
import asyncio

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Define MQTT broker settings
mqtt_broker = "127.0.0.1"  # Replace with your Mosquitto broker IP
mqtt_topic = "boat/telemetry"

# Initialize the MQTT client
mqtt_client = mqtt.Client(client_id="TelemetryToWebSocket")


def on_message(client, userdata, message):
    payload = message.payload.decode()
    try:
        telemetry_data = json.loads(payload)
        # Wrap the payload in an array
        socketio.emit("update_data", json.dumps(telemetry_data))
        print("Forwarded data to WebSocket:", telemetry_data)
    except json.JSONDecodeError as e:
        print("Invalid JSON payload:", e)


# Set up MQTT client and subscribe to the topic
mqtt_client.on_message = on_message
mqtt_client.connect(mqtt_broker, 1883, 60)
mqtt_client.subscribe(mqtt_topic)
mqtt_client.loop_start()

# Route for serving the main page
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
