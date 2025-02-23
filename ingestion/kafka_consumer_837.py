"""
Kafka Consumer for processing EDI 837 Claims processing.

- reads the claims data from Kafka topic 'claims_data'.
- writes received messages to a staging JSON file for PySpark ETL processing. 

"""

from kafka import KafkaConsumer
import json

KAFKA_BROKER ="localhost:9092"
TOPIC = "claims_data"
OUTPUT_FILE = "data_samples/staging_claims.json"

consumer = KafkaConsumer(
    TOPIC, 
    bootstrap_servers=KAFKA_BROKER, 
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset="earliest"
)

print("Listening for new claims...")

with open(OUTPUT_FILE, "w") as f:
    for message in consumer:
        claim = message.value
        json.dump(claim, f)
        f.write("\n")
        print(f"📩 Received and stored claim: {claim}")
