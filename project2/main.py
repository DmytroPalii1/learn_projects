from database import User, engine, create_db_and_tables

from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Core API", lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session



@app.post("/users", response_model=User, status_code= status.HTTP_201_CREATED)
def create_user(user: User, session: Session = Depends(get_session)):
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users", response_model=List[User])
def read_users(session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    return users

@app.get("/users{user_id}", response_model=User)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user

@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_data: User, session: Session=Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    db_user.username = user_data.username
    db_user.email = user_data.email

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session=Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    session.delete(db_user)
    session.commit()
    return None
