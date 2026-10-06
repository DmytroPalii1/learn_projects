from sqlmodel import Field, SQLModel, Relationship
from schemes import UserBase

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str
    hashed_password: str
    projects: list["Project"] = Relationship(back_populates="owner")

class Project(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str | None=None
    owner_id: int = Field(foreign_key="user.id")
    owner: User | None = Relationship(back_populates="projects")
