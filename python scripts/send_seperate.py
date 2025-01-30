import pandas as pd
import time
import paho.mqtt.client as mqtt
import json
import math

# Load telemetry data from Excel
df = pd.read_csv("seatrial.csv")  # Replace with your file path

# Set up MQTT client
mqtt_client = mqtt.Client(client_id = "ExcelTelemetryPublisher")
mqtt_client.connect("localhost", 1884, 60)

# Publish each row of telemetry data as an MQTT message

for index, row in df.iterrows():
# Convert row to dictionary and handle NaN values
    telemetry_data = {k: (v if not (isinstance(v, float) and math.isnan(v)) else None) for k, v in row.to_dict().items()}
    
    # Publish each telemetry item to a separate topic
    for key, value in telemetry_data.items():
        topic = f"boat/telemetry/{key}"  # Create unique topic for each field
        mqtt_client.publish(topic, value)
        print(f"Published to {topic}: {key} = {value}")

    time.sleep(1)  # Adjust delay as needed to simulate real-time

mqtt_client.loop_start()