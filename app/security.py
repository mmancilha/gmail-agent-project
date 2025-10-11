from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Load the key from the environment or use a default (NOT RECOMMENDED FOR PRODUCTION)
# To generate a new key, run: Fernet.generate_key().decode()
key_str = os.getenv("FERNET_KEY", "b'u2Pz_AL2o_bVSEas_8Ge-xPEw22a2i-pSStkEL3a4D4='")
FERNET_KEY = key_str.encode()

cipher_suite = Fernet(FERNET_KEY)

def encrypt_data(data: str) -> bytes:
    """Encrypts a string."""
    return cipher_suite.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypts bytes back to a string."""
    return cipher_suite.decrypt(encrypted_data).decode()

