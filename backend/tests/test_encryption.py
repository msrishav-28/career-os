"""
Token encryption tests.

Per TESTING_STRATEGY.md — Critical Path (100% Coverage Required):
  - Encrypt/decrypt roundtrip works
  - Encrypted value differs from original
  - Cannot decrypt with wrong key
"""
import pytest
import os


class TestTokenEncryption:
    """Test Fernet-based token encryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Encrypt a token and decrypt it back to the original."""
        from security.encryption import encrypt_token, decrypt_token

        original = "sk-linkedin-session-cookie-abc123"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)

        assert decrypted == original

    def test_encrypted_differs_from_original(self):
        """Encrypted value must differ from plaintext."""
        from security.encryption import encrypt_token

        original = "my-secret-api-key"
        encrypted = encrypt_token(original)

        assert encrypted != original
        assert len(encrypted) > len(original)

    def test_different_inputs_different_outputs(self):
        """Different inputs should produce different encrypted values."""
        from security.encryption import encrypt_token

        enc1 = encrypt_token("token-one")
        enc2 = encrypt_token("token-two")

        assert enc1 != enc2

    def test_empty_string(self):
        """Empty strings should encrypt/decrypt correctly."""
        from security.encryption import encrypt_token, decrypt_token

        encrypted = encrypt_token("")
        decrypted = decrypt_token(encrypted)
        assert decrypted == ""

    def test_unicode_content(self):
        """Unicode content should survive roundtrip."""
        from security.encryption import encrypt_token, decrypt_token

        original = "安全なトークン 🔐"
        encrypted = encrypt_token(original)
        decrypted = decrypt_token(encrypted)
        assert decrypted == original

    def test_wrong_key_cannot_decrypt(self):
        """Cannot decrypt with a different key."""
        from security.encryption import encrypt_token
        from cryptography.fernet import Fernet, InvalidToken

        encrypted = encrypt_token("secret-value")

        # Try to decrypt with a different key
        wrong_key = Fernet.generate_key()
        wrong_fernet = Fernet(wrong_key)

        with pytest.raises(InvalidToken):
            wrong_fernet.decrypt(encrypted.encode())

    def test_key_rotation(self):
        """Key rotation should still decrypt old tokens."""
        from security.encryption import TokenEncryption

        enc = TokenEncryption()

        old_encrypted = enc.encrypt("old-secret")

        # Rotate key
        new_key = enc.rotate_key()

        # Old token should still decrypt
        decrypted = enc.decrypt(old_encrypted)
        assert decrypted == "old-secret"

        # New encryptions should also work
        new_encrypted = enc.encrypt("new-secret")
        assert enc.decrypt(new_encrypted) == "new-secret"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
