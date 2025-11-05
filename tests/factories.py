import factory
from factory.fuzzy import FuzzyChoice

from src.enums import ToDoStatus
from src.models import ToDo, User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')


class ToDoFactory(factory.Factory):
    class Meta:
        model = ToDo

    title = factory.Faker('text')
    description = factory.Faker('text')
    status = FuzzyChoice(ToDoStatus)
    user_id = factory.SubFactory(UserFactory)
