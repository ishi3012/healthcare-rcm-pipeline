"""
Unified Kafka Producer for EDI 837 (Claims) & EDI 835 (Denials) with Interleaving

Goal:
- Reads EDI 837 (claims) and EDI 835 (denials) together.
- Ensures denial reasons appear correctly for denied/partially denied claims.
- Reads billed_amount and paid_amount directly from the 835 file instead of generating randomly.

"""

import json
import time
import random
from kafka import KafkaProducer

# Kafka setup
KAFKA_BROKER = 'localhost:9092'
CLAIMS_TOPIC = 'claims_data'
DENIALS_TOPIC = 'denials_data'

# Data files
EDI_837_FILE = "data_samples/edi_837_sample.txt"
EDI_835_FILE = "data_samples/edi_835_sample.txt"

# List of realistic denial reason codes
DENIAL_REASONS = ["CO-45", "CO-97", "PR-1", "OA-23", "CO-16", "CO-29", "PI-204", "CO-11"]

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def interleave_and_send():
    """
    Reads claims (EDI 837) and denials (EDI 835) simultaneously and sends messages to Kafka.
    Ensures denial reasons are included where applicable.
    """
    try:
        # Open both files at the same time
        with open(EDI_837_FILE, "r") as claims_file, open(EDI_835_FILE, "r") as denials_file:
            while True:
                claim_line = claims_file.readline().strip()
                denial_line = denials_file.readline().strip()

                # Process a claim message
                if claim_line and claim_line.startswith("CLM*"):
                    fields = claim_line.split("*")
                    claim_data = {
                        "claim_id": fields[1],
                        "billed_amount": float(fields[2]) if fields[2].replace('.', '', 1).isdigit() else 0.0,
                        "status": "Submitted"
                    }
                    producer.send(CLAIMS_TOPIC, value=claim_data)
                    print(f"Sent Claim: {claim_data}")

                # Process a denial message
                if denial_line and denial_line.startswith("CLP*"):
                    fields = denial_line.split("*")

                    try:
                        billed_amount = float(fields[3])  # Extract billed amount from file
                        paid_amount = float(fields[4]) if fields[4].replace('.', '', 1).isdigit() else 0.0  # Extract paid amount
                    except (IndexError, ValueError):
                        print(f"Error processing denial record: {denial_line}")
                        continue  
                    # Determine payment status
                    if paid_amount == 0:
                        status = "Fully Denied"
                        denial_reason = random.choice(DENIAL_REASONS)
                    elif paid_amount < billed_amount:
                        status = "Partially Denied"
                        denial_reason = random.choice(DENIAL_REASONS)
                    else:
                        status = "Paid Fully"
                        denial_reason = ""  # Fully paid claims have no denial reason

                    denial_data = {
                        "claim_id": fields[1],
                        "billed_amount": billed_amount,
                        "paid_amount": paid_amount,
                        "denial_reason": denial_reason,
                        "status": status
                    }
                    producer.send(DENIALS_TOPIC, value=denial_data)
                    print(f"Sent Denial: {denial_data}")

                # Simulate real-time ingestion delay
                time.sleep(1)

                # Stop when both files are completely read
                if not claim_line and not denial_line:
                    break

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except IndexError:
        print("Error: Invalid data format in EDI files. Please check file structure.")

# Run the producer with interleaved processing
interleave_and_send()
