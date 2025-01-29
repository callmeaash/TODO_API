from sqlmodel import SQLModel, Field
from pydantic import BaseModel


# Database table to store user info
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(..., description="Username is required.")
    password: str = Field(..., description="Password is required.")


# Database model to store tasks info
class Todo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(..., description="Title is required")
    description: str = Field(default=None)
    completed: str = Field(default="false")
    user_id: int = Field(foreign_key="user.id", description="Reference to User ID")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class TodoRead(BaseModel):
    id: int
    title: str
    description: str = None
    completed: str


class ReadUser(BaseModel):
    username: str
