import os, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_data(aes_key, data):
    aes = AESGCM(aes_key)
    nonce = os.urandom(12)

    plaintext = json.dumps(data).encode()
    ciphertext = aes.encrypt(nonce, plaintext, None)

    return {
        "ciphertext": ciphertext.hex(),
        "nonce": nonce.hex()
    }


def decrypt_data(aes_key, enc):
    aes = AESGCM(aes_key)
    plaintext = aes.decrypt(
        bytes.fromhex(enc["nonce"]),
        bytes.fromhex(enc["ciphertext"]),
        None
    )
    return json.loads(plaintext)
