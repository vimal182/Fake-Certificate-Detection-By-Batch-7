# blockchain/crypto_utils.py

import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

KEYS_DIR = "blockchain/keys"

def generate_keys(institution_id):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()

    os.makedirs(KEYS_DIR, exist_ok=True)

    with open(f"{KEYS_DIR}/{institution_id}_private.pem", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(f"{KEYS_DIR}/{institution_id}_public.pem", "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))


def load_private_key(institution_id):
    with open(f"{KEYS_DIR}/{institution_id}_private.pem", "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )


def load_public_key(institution_id):
    with open(f"{KEYS_DIR}/{institution_id}_public.pem", "rb") as f:
        return serialization.load_pem_public_key(
            f.read(),
            backend=default_backend()
        )


def sign_data(private_key, data):
    return private_key.sign(
        data.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def verify_signature(public_key, data, signature):
    try:
        public_key.verify(
            signature,
            data.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except:
        return False