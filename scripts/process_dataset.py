import json
import hashlib
import time
from collections import defaultdict

from fhir_reader2 import read_fhir_dataset
from key_derivation import derive_aes_key
from encryption import encrypt_data
from blockchain2 import create_block  # modified version (given below)

DATASET_PATH = "dataset/"
PRIVATE_KEY_PATH = "keys/hospital_private.pem"
MAX_FILES = 1000


# -------------------------------
# Extract Patient ID
# -------------------------------
def extract_patient_id(resource):
    if resource.get("resourceType") == "Patient":
        return resource.get("id")

    ref = (
        resource.get("subject", {}).get("reference")
        or resource.get("patient", {}).get("reference")
    )

    if ref and "urn:uuid:" in ref:
        return ref.split("urn:uuid:")[-1]

    return None


# -------------------------------
# Group Records by Patient
# -------------------------------
def group_by_patient(bundles):
    patient_map = defaultdict(list)

    for bundle in bundles:
        if bundle.get("resourceType") == "Bundle":
            for entry in bundle.get("entry", []):
                res = entry.get("resource", {})
                pid = extract_patient_id(res)
                if pid:
                    patient_map[pid].append(res)

    return patient_map


# -------------------------------
# MAIN EXECUTION
# -------------------------------
print(f"📂 Reading up to {MAX_FILES} FHIR files...")
bundles = read_fhir_dataset(DATASET_PATH, MAX_FILES)
patients = group_by_patient(bundles)

print(f"👥 Total Patients Found: {len(patients)}")

with open(PRIVATE_KEY_PATH, "rb") as f:
    hospital_private_key = f.read()

encrypted_storage = []
blockchain_chain = []

total_start = time.perf_counter()
total_encryption_time = 0.0

for idx, (pid, records) in enumerate(patients.items(), start=1):
    print(f"\n🔐 [{idx}/{len(patients)}] Processing Patient: {pid}")

    # Key Derivation (NOT counted in encryption time)
    aes_key = derive_aes_key(pid, hospital_private_key)

    # Measure PURE Encryption Time Only
    start_enc = time.perf_counter()

    encrypted = encrypt_data(
        aes_key,
        {"patient_id": pid, "records": records}
    )

    enc_time = time.perf_counter() - start_enc
    total_encryption_time += enc_time

    print(f"⏱ Encryption Time: {enc_time:.6f} sec")

    # Hash Generation
    data_hash = hashlib.sha256(
        (encrypted["ciphertext"] + encrypted["nonce"]).encode()
    ).hexdigest()

    # Create blockchain block (in memory only)
    block = create_block(blockchain_chain, data_hash)
    blockchain_chain.append(block)

    encrypted_storage.append({
        "patient_hash": hashlib.sha256(pid.encode()).hexdigest(),
        "encrypted_data": encrypted
    })


total_time = time.perf_counter() - total_start

print("\n================ PERFORMANCE REPORT ================")
print(f"🚀 Total Pipeline Time: {total_time:.6f} seconds")
print(f"🔐 Total Pure Encryption Time: {total_encryption_time:.6f} seconds")
print(f"📊 Avg Encryption Time per Patient: "
      f"{total_encryption_time/len(patients):.6f} sec")
print("===================================================")

# Write files ONCE (not inside loop)

with open("encrypted_storage.json", "w") as f:
    json.dump(encrypted_storage, f)

with open("blockchain.json", "w") as f:
    json.dump(blockchain_chain, f)


