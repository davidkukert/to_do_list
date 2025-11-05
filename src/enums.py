from enum import Enum


class ToDoStatus(str, Enum):
    DRAFT = 'draft'
    TODO = 'todo'
    DOING = 'doing'
    DONE = 'done'
    TRASH = 'trash'
