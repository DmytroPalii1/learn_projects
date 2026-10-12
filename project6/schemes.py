from sqlmodel import SQLModel

class UserBase(SQLModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int 

class ProjectCreate(SQLModel):
    title : str
    description: str | None = None

class ProjectRead(SQLModel):
    id: int
    title: str
    description: str | None
    owner_id: int

class ProjectUpdate(SQLModel):
    title: str | None = None
    description: str | None = None