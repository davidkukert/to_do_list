from http import HTTPStatus


async def test_index_root(client):
    response = await client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == dict(message='Welcome, the To Do List')
