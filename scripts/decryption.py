import json, hashlib, time
from datetime import datetime
from key_derivation import derive_aes_key
from encryption import decrypt_data

PATIENT_ID = (input("Enter Patient ID: "))

def calculate_age(birth_date):
    birth = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    return today.year - birth.year - (
        (today.month, today.day) < (birth.month, birth.day)
    )

def print_patient_report(data):
    name = age = gender = "N/A"
    conditions, medications, observations = [], [], []

    for r in data["records"]:
        t = r.get("resourceType")

        if t == "Patient":
            n = r.get("name", [{}])[0]
            name = " ".join(n.get("given", [])) + " " + n.get("family", "")
            gender = r.get("gender", "N/A")
            if r.get("birthDate"):
                age = calculate_age(r["birthDate"])

        elif t == "Condition":
            conditions.append(r["code"]["coding"][0]["display"])

        elif t == "MedicationRequest":
            medications.append(
                r["medicationCodeableConcept"]["coding"][0]["display"]
            )

        elif t == "Observation":
            obs = r["code"]["coding"][0]["display"]
            value = "N/A"

            if "valueQuantity" in r:
                v = r["valueQuantity"]
                value = f"{v.get('value')} {v.get('unit','')}"
            elif "valueCodeableConcept" in r:
                value = r["valueCodeableConcept"].get("text") or \
                        r["valueCodeableConcept"]["coding"][0]["display"]
            elif "valueString" in r:
                value = r["valueString"]
            elif "valueBoolean" in r:
                value = str(r["valueBoolean"])
            elif "valueInteger" in r:
                value = str(r["valueInteger"])

            observations.append(f"{obs} : {value}")

    print("\n================ PATIENT DETAILS ================\n")
    print(f"Name   : {name}")
    print(f"Age    : {age}")
    print(f"Gender : {gender}")

    print("\nConditions:")
    for c in set(conditions):
        print(f"- {c}")

    print("\nMedications:")
    for m in set(medications):
        print(f"- {m}")

    print("\nObservations:")
    for o in observations:
        print(f"- {o}")

    print("\n=================================================")

with open("keys/hospital_private.pem", "rb") as f:
    hospital_private_key = f.read()

with open("encrypted_storage.json") as f:
    storage = json.load(f)

for entry in storage:
    if entry["patient_hash"] == hashlib.sha256(PATIENT_ID.encode()).hexdigest():

        start = time.perf_counter()
        aes_key = derive_aes_key(PATIENT_ID, hospital_private_key)
        decrypted = decrypt_data(aes_key, entry["encrypted_data"])
        dec_time = time.perf_counter() - start

        print(f"\n⏱️ Decryption Time: {dec_time:.6f} seconds")
        print_patient_report(decrypted)
        break
else:
    print("❌ No data found for patient")
