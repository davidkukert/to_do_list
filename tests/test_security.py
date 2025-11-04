import pytest
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from src.security import hash_password, verify_password

pwd_context = PasswordHash.recommended()


def test_hash_returns_different_values_for_same_password():
    password = 'minha_senha_segura'
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2
    assert hash1.startswith('$')


def test_verify_password_success():
    password = 'senha123'
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    password = 'senha123'
    hashed = hash_password(password)
    assert verify_password('outra_senha', hashed) is False


def test_hash_and_verify_consistency():
    password = 'teste_consistencia'
    hashed = hash_password(password)
    assert pwd_context.verify(password, hashed)


def test_hash_output_is_string():
    hashed = hash_password('abc')
    assert isinstance(hashed, str)


def test_verify_invalid_hash_format():
    with pytest.raises(UnknownHashError):
        verify_password('abc', 'hash_invalido')
