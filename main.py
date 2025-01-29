from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from models import User, Token, Todo
from database import init_db, SessionDep
from typing import Annotated
from utils import hash_password, verify_password
from sqlmodel import select
from datetime import timedelta
from auth_utils import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user

app = FastAPI()

init_db()


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


@app.post("/auth/login")
def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
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


@app.get("/users/me")
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@app.put("/todos")
def create_todos(current_user: Annotated[User, Depends(get_current_user)], todo: Todo, session: SessionDep):
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
