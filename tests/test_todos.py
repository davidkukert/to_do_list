import uuid
from http import HTTPStatus

from sqlalchemy import select

from src.enums import ToDoStatus
from src.models import ToDo
from tests.factories import ToDoFactory


async def test_create_todo(client, token):
    response = await client.post(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test todo',
            'description': 'Test todo description',
            'status': 'draft',
        },
    )
    data = response.json()['data']
    assert data['title'] == 'Test todo'
    assert data['description'] == 'Test todo description'
    assert data['status'] == 'draft'


async def test_list_todos_should_return_5_todos(session, client, user, token):
    todos = await session.scalars(select(ToDo).where(ToDo.user_id == user.id))
    for todo in todos.all():
        await session.delete(todo)
    await session.commit()
    expected_todos = 5
    session.add_all(ToDoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = await client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['data']) == expected_todos


async def test_list_todos_filter_title_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        ToDoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    await session.commit()

    response = await client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['data']) == expected_todos


async def test_list_todos_filter_description_should_return_5_todos(
    session, user, client, token
):
    todos = await session.scalars(select(ToDo).where(ToDo.user_id == user.id))
    for todo in todos.all():
        await session.delete(todo)
    await session.commit()
    expected_todos = 5
    session.add_all(
        ToDoFactory.create_batch(5, user_id=user.id, description='description')
    )
    await session.commit()

    response = await client.get(
        '/todos/?description=desc',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['data']) == expected_todos


async def test_list_todos_filter_status_should_return_5_todos(
    session, user, client, token
):
    todos = await session.scalars(select(ToDo).where(ToDo.user_id == user.id))
    for todo in todos.all():
        await session.delete(todo)
    await session.commit()
    expected_todos = 5
    session.add_all(
        ToDoFactory.create_batch(5, user_id=user.id, status=ToDoStatus.DRAFT)
    )
    await session.commit()

    response = await client.get(
        '/todos/?status=draft',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['data']) == expected_todos


async def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        ToDoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            status=ToDoStatus.DONE,
        )
    )

    session.add_all(
        ToDoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            status=ToDoStatus.TODO,
        )
    )
    await session.commit()

    response = await client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['data']) == expected_todos


async def test_patch_todo_error(client, token, session, another_user):
    todo = ToDoFactory(user_id=another_user.id, description='description')
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    response = await client.patch(
        f'/todos/{todo.id}',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_patch_todo(session, client, user, token):
    todo = ToDoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = await client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['data']['title'] == 'teste!'


async def test_patch_todo_done(session, client, user, token):
    todo = ToDoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = await client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!', 'status': 'done'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['data']['title'] == 'teste!'
    assert response.json()['data']['status'] == 'done'


async def test_delete_todo(session, client, user, token):
    todo = ToDoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    response = await client.delete(
        f'/todos/{todo.id}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'message': 'Task has been deleted successfully.'
    }


async def test_delete_todo_error(client, token):
    response = await client.delete(
        f'/todos/{uuid.uuid7()}', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}
