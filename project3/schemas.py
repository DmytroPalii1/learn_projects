from sqlmodel import SQLModel

class UserBase(SQLModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int 