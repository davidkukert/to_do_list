from http import HTTPStatus
from uuid import uuid7

import pytest
from fastapi import HTTPException
from freezegun import freeze_time
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from src.security.auth import create_access_token, get_current_user
from src.security.hash import hash_password, verify_password

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


async def test_get_current_user_valid_token(session, user):
    valid_token = create_access_token({'sub': str(user.id)})

    current_user = await get_current_user(session=session, token=valid_token)

    assert current_user.id == user.id
    assert current_user.username == user.username


async def test_get_current_user_id_not_found(session):
    invalid_token = create_access_token({'sub': str(uuid7())})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(session=session, token=invalid_token)

    assert excinfo.value.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in excinfo.value.detail


async def test_get_current_user_expired_token(session, user):
    with freeze_time('2023-07-14 12:00:00'):
        expired_token = create_access_token({
            'sub': str(user.id),
        })

    with freeze_time('2023-07-14 12:50:00'):
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(session=session, token=expired_token)

        assert excinfo.value.status_code == HTTPStatus.UNAUTHORIZED
        assert 'Could not validate credentials' in excinfo.value.detail


async def test_get_current_user_sub_not_found(session):
    invalid_token = create_access_token({})
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(session=session, token=invalid_token)

    assert excinfo.value.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in excinfo.value.detail


async def test_get_current_user_invalid_token(session):
    invalid_token = 'invalid_token'
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(session=session, token=invalid_token)

    assert excinfo.value.status_code == HTTPStatus.UNAUTHORIZED
    assert 'Could not validate credentials' in excinfo.value.detail
