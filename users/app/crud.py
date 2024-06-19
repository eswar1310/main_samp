from sqlalchemy.orm import Session
from app.models import User
from . import models, schemas
from app.schemas import UserCreate
from typing import List, Tuple
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str) -> models.User:
    return db.query(User).filter(User.email == email).first()

def hash_password(password: str) -> str:
    # Hash the password using bcrypt
    hashed_password = pwd_context.hash(password)
    return hashed_password

def create_user(db: Session, user_data: UserCreate) -> models.User:
    hashed_password = hash_password(user_data.password)
    db_user = User(firstname=user_data.firstname, lastname=user_data.lastname, email=user_data.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_data: schemas.UserUpdate) -> models.User:
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return None
    
    # Update user data
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
def get_users(db: Session, skip: int = 0, limit: int = 10) -> Tuple[List[models.User], int]:
    users = db.query(models.User).offset(skip).limit(limit).all()
    total_users = db.query(models.User).count()  # Count the total number of users
    return users, total_users

def get_user(db: Session, user_id: int) -> models.User:
    return db.query(models.User).filter(models.User.id == user_id).first()
 
def get_total_users(db: Session) -> int:
    return db.query(models.User).count()

def user_to_dict(user: models.User):
    return {
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
    }
