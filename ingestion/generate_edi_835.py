"""
Generate Mock EDI 835 (Denials & Remittance) Data

Goal:
- Generates synthetic EDI 835 files with realistic remittance & denial information.
- Each record includes claim ID, billed amount, paid amount, and denial reasons.
- Fixes issue where "Fully Denied" or "Partially Denied" claims didn't always match denial reasons correctly.

"""

import random
from faker import Faker

fake = Faker()

# List of realistic denial reason codes
DENIAL_REASONS = ["CO-45", "CO-97", "PR-1", "OA-23", "CO-16", "CO-29", "PI-204", "CO-11"]

def generate_edi_835(num_claims=100):
    """Generates a mock EDI 835 remittance/denials file"""
    edi_lines = [
        "ISA*00*          *00*          *ZZ*PAYERID       *ZZ*PROVIDERID    *230101*1253*U*00501*000000002*0*P*:~",
        "GS*HP*PAYERID*PROVIDERID*20230101*1253*2*X*005010X221A1~"
    ]
    
    for _ in range(num_claims):
        claim_id = f"CLAIM{random.randint(100000, 999999)}"
        patient_id = fake.uuid4()
        provider = fake.company()
        billed_amount = round(random.uniform(100, 5000), 2)  # Original billed amount

        # Determine payment status with fixed logic
        status_probabilities = {"Fully Denied": 0.3, "Partially Denied": 0.4, "Paid Fully": 0.3}
        payment_type = random.choices(list(status_probabilities.keys()), weights=status_probabilities.values())[0]
        print(f" Status = {payment_type}")
        
        if payment_type == "Fully Denied":
            paid_amount = 0.00
            denial_reason = random.choice(DENIAL_REASONS)  
        elif payment_type == "Partially Denied":
            paid_amount = round(billed_amount * random.uniform(0.3, 0.9), 2)  
            denial_reason = random.choice(DENIAL_REASONS) 
        else:  # Paid Fully
            paid_amount = billed_amount
            denial_reason = ""  

        edi_lines.append(f"ST*835*{claim_id}~")
        edi_lines.append(f"BPR*I*{paid_amount}*C*ACH*CTX*01*999999999*DA*12345678*999999999*DA*87654321~")
        edi_lines.append(f"TRN*1*{claim_id}*PAYERID~")
        edi_lines.append(f"REF*EV*{patient_id}~")
        edi_lines.append(f"DTM*405*20230101~")
        edi_lines.append(f"CLP*{claim_id}*{payment_type}*{billed_amount}*{paid_amount}***12*PROVIDERID~")

        # Add denial reason only when applicable
        if payment_type in ["Fully Denied", "Partially Denied"]:
            denied_amount = round(billed_amount - paid_amount, 2)
            edi_lines.append(f"CAS*CO*{denial_reason}*{denied_amount}~")

        edi_lines.append(f"SE*6*{claim_id}~")

    edi_lines.append("GE*1*2~")
    edi_lines.append("IEA*1*000000002~")

    return "\n".join(edi_lines)

def count_edi_records(file_path, record_type):
    """Counts the number of records in an EDI file based on ST segments"""
    with open(file_path, "r") as file:
        content = file.readlines()

    record_count = sum(1 for line in content if line.startswith(f"ST*{record_type}"))
    print(f"\n {record_type} Records in {file_path}: {record_count}\n")

if __name__ == "__main__":
    # Write to file
    raw_file_path = "data_samples/edi_835_sample.txt"
    with open(raw_file_path, "w") as f:
        f.write(generate_edi_835(100))
    print("\n✅ Mock EDI 835 remittance/denials file generated: edi_835_sample.txt")
    count_edi_records(raw_file_path, "835")
