from fastapi import FastAPI

from src.routers import auth, todos, users

app = FastAPI(
    title='To Do List',
    description='API for To Do List',
    version='1.0.0',
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(todos.router)


@app.get('/')
async def index_root():
    return dict(message='Welcome, the To Do List')
