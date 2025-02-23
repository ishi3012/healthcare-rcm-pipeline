"""
Kafka Consumer for EDI 835 (Denials Processing)

Goal:
- Reads denials data from Kafka topic `denials_data`.
- Writes received messages to a staging JSON file for PySpark ETL processing.
"""
from kafka import KafkaConsumer
import json

# Kafka setup
KAFKA_BROKER = 'localhost:9092'
TOPIC = 'denials_data'
OUTPUT_FILE = "data_samples/staging_denials.json"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest'
)

print("Listening for new denials...")
with open(OUTPUT_FILE, "w") as f:
    for message in consumer:
        denial_record = message.value
        json.dump(denial_record, f)
        f.write("\n")
        print(f"Received and stored denial: {denial_record}")
