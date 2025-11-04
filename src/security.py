from pwdlib import PasswordHash

pwd_ctx = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a plaintext password."""
    return pwd_ctx.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return pwd_ctx.verify(password, hashed)
