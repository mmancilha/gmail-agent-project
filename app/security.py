from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Load the key from the environment
key_str = os.getenv("FERNET_KEY")

# --- DEBUGGING STEP ---
# Vamos imprimir a chave para termos a certeza de qual está a ser usada.
print("---" * 10)
if key_str:
    print(f"DEBUG: FERNET_KEY loaded successfully from .env: {key_str[:5]}...")
else:
    print("FATAL DEBUG: FERNET_KEY was NOT FOUND in the .env file!")
print("---" * 10)
# --- END DEBUGGING STEP ---

# Ensure the key is not None before encoding
if not key_str:
    raise ValueError("FERNET_KEY environment variable not set. Please check your .env file.")

FERNET_KEY = key_str.encode()
cipher_suite = Fernet(FERNET_KEY)

def encrypt_data(data: str) -> bytes:
    """Encrypts a string."""
    return cipher_suite.encrypt(data.encode())

def decrypt_data(encrypted_data: bytes) -> str:
    """Decrypts bytes back to a string."""
    return cipher_suite.decrypt(encrypted_data).decode()