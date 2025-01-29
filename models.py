from sqlmodel import SQLModel, Field
from pydantic import BaseModel


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(..., description="Username is required.")
    password: str = Field(..., description="Password is required.")


class Todo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(..., description="Title is required")
    description: str = Field(default=None)
    user_id: int = Field(foreign_key="user.id", description="Reference to User ID")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
