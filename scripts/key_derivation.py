import hashlib

def derive_aes_key(patient_id, hospital_private_key_bytes):
    combined = patient_id.encode() + hospital_private_key_bytes
    return hashlib.sha256(combined).digest()
