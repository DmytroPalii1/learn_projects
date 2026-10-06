from datetime import datetime, timedelta, timezone
import jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlmodel import Session, select
import bcrypt 

from database import engine, create_db_and_tables
from models import User, Project
from schemes import UserCreate, UserRead, ProjectCreate, ProjectRead, ProjectUpdate

SECRET_KEY = "super_secret_saas_key_change_this_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="SaaS Core API", lifespan=lifespan)

def get_session():
    with Session(engine) as session:
        yield session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(
    token: str = Depends(oauth2_scheme), 
    session: Session = Depends(get_session)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
        
    return user


# Endpoints

@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, session: Session = Depends(get_session)):

   existing_user = session.exec(select(User).where(User.username == user_in.username)).first()
   if existing_user:
           raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail="Username already registered"
           )

   hashed_pwd = hash_password(user_in.password)
   db_user = User(
           username=user_in.username,
           email=user_in.email,
           hashed_password=hashed_pwd
       )
    
   session.add(db_user)
   session.commit()
   session.refresh(db_user)
   return db_user


@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer"
    }


@app.get("/users/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


@app.post("/projects", response_model=ProjectRead)
def create_project(
    project_data: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_project = Project(
        title=project_data.title,
        description=project_data.description,
        owner_id=current_user.id, 
    )

    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    return db_project



@app.get("/projects", response_model=list[ProjectRead])
def read_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(Project).where(Project.owner_id == current_user.id)

    projects = session.exec(statement).all()

    return projects


@app.get("/projects/{project_id}", response_model=ProjectRead)
def read_a_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    statement = select(Project).where(Project.id == project_id, Project.owner_id == current_user.id)

    project = session.exec(statement).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    return project


@app.patch("/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(Project).where(
        Project.id == project_id, Project.owner_id == current_user.id
    )
    db_project = session.exec(statement).first()

    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    update_data = project_data.model_dump(exclude_unset=True)
    db_project.sqlmodel_update(update_data)

    session.add(db_project)
    session.commit()
    session.refresh(db_project)

    return db_project


@app.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    statement = select(Project).where(
        Project.id == project_id, Project.owner_id == current_user.id
    )
    db_project = session.exec(statement).first()

    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    session.delete(db_project)
    session.commit()

    return None