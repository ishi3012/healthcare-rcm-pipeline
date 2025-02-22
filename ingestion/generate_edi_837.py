
import random
from faker import Faker

fake = Faker()

def generate_edi_837(num_claims=100):
    """Generates a mock EDI 837 claims file"""
    edi_lines = [
        "ISA*00*          *00*          *ZZ*SENDERID      *ZZ*RECEIVERID    *230101*1253*U*00501*000000001*0*P*:~",
        "GS*HC*SENDERID*RECEIVERID*20230101*1253*1*X*005010X222A1~"
    ]
    
    for _ in range(num_claims):
        claim_id = f"CLAIM{random.randint(100000, 999999)}"
        patient_id = fake.uuid4()
        provider = fake.company()
        procedure_code = random.choice(["99213", "99214", "99397"])
        diagnosis_code = random.choice(["E11.9", "I10", "J45.909"])
        billed_amount = round(random.uniform(100, 5000), 2)

        edi_lines.append(f"ST*837*{claim_id}~")
        edi_lines.append(f"BHT*0019*00*{claim_id}*20230101*1253*CH~")
        edi_lines.append(f"NM1*IL*1*{fake.last_name()}*{fake.first_name()}****MI*{patient_id}~")
        edi_lines.append(f"NM1*PR*2*{provider}*****PI*PAYERID~")
        edi_lines.append(f"CLM*{claim_id}*{billed_amount}***11:B:1*Y*A*Y*I~")
        edi_lines.append(f"HI*ABK:{diagnosis_code}~")
        edi_lines.append(f"SE*6*{claim_id}~")

    edi_lines.append("GE*1*1~")
    edi_lines.append("IEA*1*000000001~")

    return "\n".join(edi_lines)

# # Write to file
# with open("data_samples/edi_837_sample.txt", "w") as f:
#     f.write(generate_edi_837())

# print("✅ Mock EDI 837 claims file generated: edi_837_sample.txt")

def count_edi_records(file_path, record_type):
    """Counts the number of records in an EDI file based on ST segments"""
    with open(file_path, "r") as file:
        content = file.readlines()

    record_count = sum(1 for line in content if line.startswith(f"ST*{record_type}"))
    print(f"\n {record_type} Records in {file_path}: {record_count}\n")


if __name__ == "__main__":
    # Write to file
    raw_file_path = "data_samples/edi_837_sample.txt"
    with open(raw_file_path, "w") as f:
        f.write(generate_edi_837(100))
    print("\n Mock EDI 835 remittance/denials file generated: edi_837_sample.txt")
    count_edi_records(raw_file_path,"837")