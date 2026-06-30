from __future__ import annotations
import os
import secrets
from enum import Enum
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pookiepages.exceptions import PookiePagesError

KEY_FILE = ".pookiepages.key"
NONCE_SIZE_GCM = 12
NONCE_SIZE_CHACHA = 12
IV_SIZE_CBC = 16


class EncryptionAlgorithm(str, Enum):
    AES_256_GCM = "AES_256_GCM"
    CHACHA20_POLY1305 = "CHACHA20_POLY1305"
    AES_256_CBC = "AES_256_CBC"


def _resolveKey(configured_key: str, project_root: str = ".") -> bytes:
    if configured_key:
        rawKey = configured_key.encode() if isinstance(configured_key, str) else configured_key
        # Derive a 32-byte key from whatever was provided
        import hashlib
        return hashlib.sha256(rawKey).digest()

    keyPath = os.path.join(project_root, KEY_FILE)
    if os.path.exists(keyPath):
        with open(keyPath, "rb") as keyFile:
            return bytes.fromhex(keyFile.read().strip().decode())

    # Generate a new 32-byte (256-bit) key, store as hex (64 chars)
    newKey = secrets.token_bytes(32)
    with open(keyPath, "wb") as keyFile:
        keyFile.write(newKey.hex().encode())
    print(f"pookiepages: generated new encryption key at {KEY_FILE} (keep this file secret and out of version control)")
    return newKey


def encrypt(plaintext: bytes, key: bytes, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> bytes:
    if algorithm == EncryptionAlgorithm.AES_256_GCM:
        nonce = secrets.token_bytes(NONCE_SIZE_GCM)
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
        nonce = secrets.token_bytes(NONCE_SIZE_CHACHA)
        chacha = ChaCha20Poly1305(key)
        ciphertext = chacha.encrypt(nonce, plaintext, None)
        return nonce + ciphertext

    if algorithm == EncryptionAlgorithm.AES_256_CBC:
        from cryptography.hazmat.primitives import padding as cryptoPadding
        iv = secrets.token_bytes(IV_SIZE_CBC)
        padder = cryptoPadding.PKCS7(128).padder()
        paddedData = padder.update(plaintext) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(paddedData) + encryptor.finalize()
        return iv + ciphertext

    raise PookiePagesError(f"Encryption failed. Unknown algorithm: {algorithm}. Use EncryptionAlgorithm enum values.")


def decrypt(ciphertext: bytes, key: bytes, algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM) -> bytes:
    if algorithm == EncryptionAlgorithm.AES_256_GCM:
        nonce = ciphertext[:NONCE_SIZE_GCM]
        data = ciphertext[NONCE_SIZE_GCM:]
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, data, None)

    if algorithm == EncryptionAlgorithm.CHACHA20_POLY1305:
        nonce = ciphertext[:NONCE_SIZE_CHACHA]
        data = ciphertext[NONCE_SIZE_CHACHA:]
        chacha = ChaCha20Poly1305(key)
        return chacha.decrypt(nonce, data, None)

    if algorithm == EncryptionAlgorithm.AES_256_CBC:
        from cryptography.hazmat.primitives import padding as cryptoPadding
        iv = ciphertext[:IV_SIZE_CBC]
        data = ciphertext[IV_SIZE_CBC:]
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        paddedPlaintext = decryptor.update(data) + decryptor.finalize()
        unpadder = cryptoPadding.PKCS7(128).unpadder()
        return unpadder.update(paddedPlaintext) + unpadder.finalize()

    raise PookiePagesError(f"Decryption failed. Unknown algorithm: {algorithm}. Use EncryptionAlgorithm enum values.")


def loadEncryptionKey(project_root: str = ".") -> tuple[bytes, EncryptionAlgorithm]:
    from flask import current_app
    try:
        dbConfig = None
        import importlib.util, sys, os
        settingsFile = current_app.config["PP_APP"].settingsFile
        settingsPath = os.path.join(project_root, settingsFile)
        if os.path.exists(settingsPath):
            spec = importlib.util.spec_from_file_location("pp_settings", settingsPath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            dbConfig = getattr(module, "DATABASE", None)
    except RuntimeError:
        dbConfig = None

    configuredKey = ""
    algorithmName = EncryptionAlgorithm.AES_256_GCM

    if dbConfig is not None:
        from pookiepages.database import DatabaseConfig
        if isinstance(dbConfig, DatabaseConfig):
            configuredKey = dbConfig.encryptionKey
            try:
                algorithmName = EncryptionAlgorithm(dbConfig.encryptionAlgorithm)
            except ValueError:
                algorithmName = EncryptionAlgorithm.AES_256_GCM

    key = _resolveKey(configuredKey, project_root)
    print(f"pookiepages: encryption on ({algorithmName.value})")
    return key, algorithmName
