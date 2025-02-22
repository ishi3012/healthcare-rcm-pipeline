import random
from faker import Faker

fake = Faker()

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
        paid_amount = round(random.uniform(50, 4000), 2)
        status = random.choice(["Denied", "Paid Partially", "Paid Fully"])
        denial_reason = random.choice(["CO-45", "CO-97", "PR-1"]) if status == "Denied" else ""

        edi_lines.append(f"ST*835*{claim_id}~")
        edi_lines.append(f"BPR*I*{paid_amount}*C*ACH*CTX*01*999999999*DA*12345678*999999999*DA*87654321~")
        edi_lines.append(f"TRN*1*{claim_id}*PAYERID~")
        edi_lines.append(f"REF*EV*{patient_id}~")
        edi_lines.append(f"DTM*405*20230101~")
        edi_lines.append(f"CLP*{claim_id}*{status}*{paid_amount}***12*PROVIDERID~")
        if denial_reason:
            edi_lines.append(f"CAS*CO*{denial_reason}*100.00~")
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
    print("\n Mock EDI 835 remittance/denials file generated: edi_835_sample.txt")
    count_edi_records(raw_file_path,"835")