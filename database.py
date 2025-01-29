from sqlmodel import create_engine, SQLModel, Session
from typing import Annotated
from fastapi import Depends

sqlite_database_name = "database.db"
DATABASE_URL = f"sqlite:///{sqlite_database_name}"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def init_db():
    SQLModel.metadata.create_all(engine)
