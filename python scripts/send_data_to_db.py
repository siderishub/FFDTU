import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure InfluxDB connection
INFLUXDB_URL = "http://localhost:8086"  # Replace with your InfluxDB URL
INFLUXDB_TOKEN = "fIrjZWeaojCHcvou1O2y3qytnUYd6gGDE7XhF2ZVCrvQsKQCbuC3P7HPJOM_aI4d4RrXz_DdvirGVnzZIT6JZQ=="      # Replace with your InfluxDB token
INFLUXDB_ORG = "docs"                   # Replace with your organization
INFLUXDB_BUCKET = "boat_telemetry"      # Replace with your bucket

influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Cache to store incoming MQTT data
data_cache = {}

# MQTT Callback for incoming messages
def on_message(client, userdata, msg):
    global data_cache
    topic = msg.topic.split("/")[-1]  # Extract the last part of the topic
    value = msg.payload.decode('utf-8').strip()
    
    # Parse numeric values and handle empty fields
    try:
        value = float(value) if value else None
    except ValueError:
        pass  # Keep it as string if it's not a number
    
    # Add to cache
    data_cache[topic] = value
    
    # Write to InfluxDB when all expected fields are present
    if len(data_cache) >= 22:  # Number of expected fields
        write_to_influxdb(data_cache)

def write_to_influxdb(data):
    # Create a Point with all fields from the cache
    point = Point("telemetry").tag("object", "boat")
    for key, value in data.items():
        if value is not None:
            point.field(key, value)
    
    # Write the Point to InfluxDB
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
    print(f"Data written to InfluxDB: {data}")

# MQTT Configuration
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect("localhost", 1884)  # Update host and port if necessary

# Subscribe to all telemetry topics
topics = [
    "boat/telemetry/current_time", "boat/telemetry/latitude", "boat/telemetry/longitude",
    "boat/telemetry/speed", "boat/telemetry/miles", "boat/telemetry/miles_lap",
    "boat/telemetry/rtc", "boat/telemetry/millis", "boat/telemetry/rpm",
    "boat/telemetry/input_voltage", "boat/telemetry/motor_watt",
    "boat/telemetry/motor_tempMosfet", "boat/telemetry/motor_tempMotor",
    "boat/telemetry/motor_current", "boat/telemetry/battery_current",
    "boat/telemetry/motor_dutyCycle", "boat/telemetry/motor_error",
    "boat/telemetry/rasp_temp", "boat/telemetry/battery_ampere",
    "boat/telemetry/battery_voltage", "boat/telemetry/charge",
    "boat/telemetry/battery_temperature", "boat/telemetry/autonomy"
]

for topic in topics:
    mqtt_client.subscribe(topic)

# Start the MQTT client loop
mqtt_client.loop_forever()
