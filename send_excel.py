import pandas as pd
import time
import paho.mqtt.client as mqtt
import json

# Load telemetry data from Excel
df = pd.read_csv("seatrial.csv")  # Replace with your file path

# Set up MQTT client
mqtt_client = mqtt.Client(client_id = "ExcelTelemetryPublisher")
mqtt_client.connect("127.0.0.1", 1883, 60)

# Publish each row of telemetry data as an MQTT message

for index, row in df.iterrows():
    telemetry_data = row.to_dict()  # Convert row to dictionary
    mqtt_client.publish("boat/telemetry", json.dumps(telemetry_data))
    print(f"Published: {telemetry_data}")
    time.sleep(1)  # Adjust delay as needed to simulate real-time

mqtt_client.loop_start()
