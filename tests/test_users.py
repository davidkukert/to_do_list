import asyncio
from http import HTTPStatus
from uuid import uuid7, uuid8

from src.schemas import UserCreateInput, UserSchema


async def test_index_users(client, user, another_user):
    response = await client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == dict(
        data=[
            dict(
                id=str(user.id),
                username=user.username,
                createdAt=user.created_at.isoformat(),
                updatedAt=user.updated_at.isoformat(),
            ),
            dict(
                id=str(another_user.id),
                username=another_user.username,
                createdAt=another_user.created_at.isoformat(),
                updatedAt=another_user.updated_at.isoformat(),
            ),
        ]
    )


async def test_get_user(client, user):
    response = await client.get(f'/users/{user.id}')
    data = UserSchema(**response.json()['data'])
    assert response.status_code == HTTPStatus.OK
    assert data == UserSchema(**user.__dict__)


async def test_get_user_not_found(client):
    response = await client.get(f'/users/{uuid8()}')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == dict(detail='User not found')


async def test_create_user(client):
    user_data = UserCreateInput(
        username=f'test1{uuid7()}', password='12345678'
    )
    response = await client.post(
        '/users/', json=user_data.model_dump(by_alias=True)
    )
    data = response.json()['data']
    assert response.status_code == HTTPStatus.CREATED
    assert data['username'] == user_data.username
    assert 'id' in data
    assert 'createdAt' in data
    assert 'updatedAt' in data


async def test_create_user_already_exists(client, user):
    response = await client.post(
        '/users/', json=dict(username=user.username, password='12345678')
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == dict(detail='Username not available')


async def test_update_user(client, user, token):
    new_username = 'updated_test'
    updated_at_before = user.updated_at

    await asyncio.sleep(5)

    response = await client.put(
        f'/users/{user.id}',
        json=dict(username=new_username, password='12345678'),
        headers=dict(Authorization=f'Bearer {token}'),
    )

    data = response.json()['data']
    assert response.status_code == HTTPStatus.OK
    assert data['username'] == new_username
    assert data['updatedAt'] != updated_at_before.isoformat()
    assert data['id'] == str(user.id)
    assert 'createdAt' in data


async def test_update_user_not_found(client, token):
    response = await client.put(
        f'/users/{uuid8()}',
        json=dict(username='non_existent_user'),
        headers=dict(Authorization=f'Bearer {token}'),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == dict(detail='User not found')


async def test_update_user_already_username_taken(
    client, user, another_user, token
):
    response = await client.put(
        f'/users/{user.id}',
        json=dict(username=another_user.username),
        headers=dict(Authorization=f'Bearer {token}'),
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == dict(detail='Username not available')


async def test_update_user_forbidden(client, another_user, token):
    response = await client.put(
        f'/users/{another_user.id}',
        json=dict(username='should_not_work'),
        headers=dict(Authorization=f'Bearer {token}'),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == dict(detail='Forbidden')


async def test_delete_user_not_found(client, another_token):
    response = await client.delete(
        f'/users/{uuid8()}',
        headers=dict(Authorization=f'Bearer {another_token}'),
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == dict(detail='User not found')


async def test_delete_user_forbidden(client, another_user, token):
    response = await client.delete(
        f'/users/{another_user.id}',
        headers=dict(Authorization=f'Bearer {token}'),
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == dict(detail='Forbidden')


async def test_delete_user(client, user, token):
    response = await client.delete(
        f'/users/{user.id}',
        headers=dict(Authorization=f'Bearer {token}'),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == dict(message='User deleted')
