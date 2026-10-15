from sqlmodel import Field, SQLModel, Relationship
from pydantic import BaseModel

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

class ProjectAnalysis(BaseModel):
    category: str = Field(description="The primary business category of the project, e.g., FinTech, AI, E-Commerce")
    complexity_score: int = Field(description="A score from 1 to 10 rating the technical complexity")
    suggested_tags: list[str] = Field(description="3 to 5 relevant technical tags")
    summary: str = Field(description="A professional one-sentence summary of the project")
