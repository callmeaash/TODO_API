from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User, Token, Todo, TodoRead, ReadUser
from database import init_db, SessionDep
from typing import Annotated, List
from utils import hash_password, verify_password
from sqlmodel import select
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError
from auth_utils import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)

app = FastAPI()

init_db()

# dependency that injects authenticated info in the route handler
CurrentUserDep = Annotated[User, Depends(get_current_user)]


# Route to register a new user
@app.post("/users")
def create_user(user: User, session: SessionDep):
    query = select(User).where(User.username == user.username)
    existing_user = session.exec(query).first()
    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User already exists"
        )
    user.password = hash_password(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"Success": "User registered successfully."}


# Route to login the user
@app.post("/auth/login")
def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep
):
    query = select(User).where(User.username == form_data.username)
    result = session.exec(query).first()
    if not result or not verify_password(form_data.password, result.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid Credentials"
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


# Route to return the current logged in user information
@app.get("/users/me", response_model=ReadUser)
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


# Route to create new tasks
@app.put("/todos")
def create_todos(
    current_user: CurrentUserDep,
    todo: Todo,
    session: SessionDep,
):
    if not todo:
        raise HTTPException(
            status_code=400,
            detail="Invalid todo data"
        )
    todo.user_id = current_user.id
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return {"success": "Todo added successfully"}


# Route to read the tasks of current active user
@app.get("/todos", response_model=List[TodoRead])
def read_todo(
    current_user: CurrentUserDep,
    session: SessionDep
):
    try:
        query = select(Todo).where(Todo.user_id == current_user.id)
        result = session.exec(query).all()
        return result
    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database Error"
        )


# Route to update certain task
@app.put("/todos/{task_id}", response_model=TodoRead)
def update_todo(
    task_id: int,
    current_user: CurrentUserDep,
    todo: Todo,
    session: SessionDep
):
    result = session.get(Todo, task_id)
    if not result:
        return HTTPException(
            status_code=404,
            detail="Task doesnot exist"
        )
    if current_user.id != result.user_id:
        raise HTTPException(
            status_code=403,
            detail="You donot have permission to update this task"
        )
    for field, value in todo.model_dump(exclude_unset=True).items():
        setattr(result, field, value)

    session.commit()
    session.refresh(result)
    return result


# Route to delete a task
@app.delete("/todos/{task_id}")
def delete_todo(
    task_id: int,
    current_user: CurrentUserDep,
    session: SessionDep
):
    result = session.get(Todo, task_id)
    if not result:
        return HTTPException(
            status_code=404,
            detail="Task doesnot exist"
        )
    if current_user.id != result.user_id:
        raise HTTPException(
            status_code=403,
            detail="You donot have permission to delete this task"
        )
    session.delete(result)
    session.commit()
    return {"Success": "Task deleted successfully"}
