from http import HTTPStatus

from freezegun import freeze_time

from src.schemas import TokenResponse


async def test_get_token(client, user):
    response = await client.post(
        '/auth/token',
        data={'username': user.username, 'password': '12345678'},
    )
    token = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


async def test_token_expired_after_time(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = await client.post(
            '/auth/token',
            data={'username': user.username, 'password': '12345678'},
        )
        assert response.status_code == HTTPStatus.OK
        token = TokenResponse(**response.json()).model_dump()

    with freeze_time('2023-07-14 12:31:00'):
        response = await client.get(
            '/auth/me',
            headers={'Authorization': f'Bearer {token["access_token"]}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


async def test_token_inexistent_user(client):
    response = await client.post(
        '/auth/token',
        data={'username': 'no_user', 'password': 'testtest'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


async def test_token_wrong_password(client, user):
    response = await client.post(
        '/auth/token',
        data={'username': user.username, 'password': 'wrong_password'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect username or password'}


async def test_refresh_token(client, token):
    response = await client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = TokenResponse(**response.json()).model_dump()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


async def test_token_expired_dont_refresh(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = await client.post(
            '/auth/token',
            data={'username': user.username, 'password': '12345678'},
        )
        assert response.status_code == HTTPStatus.OK
        token = TokenResponse(**response.json())

    with freeze_time('2023-07-14 12:31:00'):
        response = await client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token.access_token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


async def test_get_current_user(client, user, token):
    response = await client.get(
        '/auth/me',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert data['data']['id'] == str(user.id)
    assert data['data']['username'] == user.username
    assert data['data']['createdAt'] == user.created_at.isoformat()
    assert data['data']['updatedAt'] == user.updated_at.isoformat()
