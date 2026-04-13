"""
Token encryption utilities for sensitive credentials.

Used to encrypt LinkedIn session tokens and other secrets at rest,
addressing the security concerns in ELITE_REDESIGN_MASTER_PLAN.md §5.5.

Uses Fernet symmetric encryption (AES-128-CBC via cryptography library,
already available as a dependency of python-jose[cryptography]).
"""
from cryptography.fernet import Fernet, InvalidToken
from config.settings import settings
import base64
import hashlib


def _derive_key(secret: str) -> bytes:
    """
    Derive a 32-byte key from the application SECRET_KEY.

    Fernet requires a URL-safe base64-encoded 32-byte key.
    We use SHA-256 to consistently derive this from our SECRET_KEY.
    """
    digest = hashlib.sha256(secret.encode()).digest()
    return base64.urlsafe_b64encode(digest)


# Initialize cipher with the application secret
_fernet = Fernet(_derive_key(settings.SECRET_KEY))


def encrypt_token(plaintext: str) -> str:
    """
    Encrypt a sensitive token (e.g., LinkedIn session cookie).

    Args:
        plaintext: The raw token string.

    Returns:
        Base64-encoded encrypted string safe for database storage.
    """
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """
    Decrypt a previously encrypted token.

    Args:
        ciphertext: The encrypted string from the database.

    Returns:
        Original plaintext token.

    Raises:
        ValueError: If decryption fails (wrong key, corrupted data).
    """
    try:
        return _fernet.decrypt(ciphertext.encode()).decode()
    except InvalidToken as e:
        raise ValueError(f"Failed to decrypt token: {e}")


def rotate_key(old_ciphertext: str, new_secret: str) -> str:
    """
    Re-encrypt a token with a new secret key.

    Useful during key rotation per OPERATIONAL_RUNBOOK.md.

    Args:
        old_ciphertext: Token encrypted with the current key.
        new_secret: The new SECRET_KEY to encrypt with.

    Returns:
        Token encrypted with the new key.
    """
    # Decrypt with current key
    plaintext = decrypt_token(old_ciphertext)

    # Re-encrypt with new key
    new_fernet = Fernet(_derive_key(new_secret))
    return new_fernet.encrypt(plaintext.encode()).decode()
