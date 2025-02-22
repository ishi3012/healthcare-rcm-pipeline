"""
Kafka Producer for Healthcare RCM Pipeline.

Goal:
    - Simulates realtime claims ingestion.
    - Generated mock EDI 837 and sends it to a Kafka topic.
    - Runs continuously to simulate a live data stream.

Functionality:
    - Creates a Kafka producer that connects to the Kafka broker.
    - Generates synthetic healthcare claim data.
    - Sends generated claim messages to the "claims_data" kafka topic every 5 seconds.
"""

from kafka import KafkaProducer
import json
import time
import random

KAFKA_BROKER = "localhost:9092"
TOPIC = "claims_data"
DATA_FILE = "data_samples/edi_837_sample.txt"

producer = KafkaProducer(bootstrap_servers = KAFKA_BROKER, 
                        value_serializer=lambda v: json.dumps(v).encode('utf-8')
                        )

def send_mock_claims():
    """
    Reads mock claims from the EDI 837 file and sends them to Kafka.
    """

    try:
        with open(DATA_FILE, "r") as file:
            for line in file:
                if line.startswith("CLM*"):
                    fields = line.strip().split("*")
                    claim_data = {
                        "claim_id": fields[1], 
                        "biled_amount": float(fields[2]), 
                        "status":"Submitted"
                    }

                    producer.send(TOPIC, value=claim_data)
                    print(f"Sent claim: {claim_data}")
    except FileNotFoundError:
        print(f"Error: Data file {DATA_FILE} not found. Run the data generation script first.")

# count= 10
# while True:
#     if count<11:
#         send_mock_claims()
#         count +=1
#         time.sleep(5)
#     else:
#         break

while True:
    send_mock_claims()
    time.sleep(5)
    


