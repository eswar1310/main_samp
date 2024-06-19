from fastapi import Depends, FastAPI, Form, File, HTTPException, Query, status, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import HttpUrl
from typing import Tuple
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from app import crud, models, schemas, auth
from app.db import SessionLocal, engine
from app.schemas import UserListResponse

# Initialize FastAPI app
app = FastAPI()
chatbot = None
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_home(request: Request):
    with open("static/index.html") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

# JWT configuration
SECRET_KEY = "qnLtBJamm3yvY7dVGHLCDJC5zDopCtfFoyS9w_JwdaQ"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Dependency to create access token
def create_access_token(email: str, expires_delta: timedelta):
    to_encode = {"sub": email}
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dictionary to store user-specific chatbot instances
user_chatbots = {}

@app.post("/Register", response_model=Tuple[schemas.User, str])
async def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
   
    new_user = crud.create_user(db=db, user_data=user_data)
    user_dict = schemas.User.from_orm(new_user)
    return user_dict, "User registered successfully"

@app.post("/Login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = crud.get_user_by_email(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(email=user.email, expires_delta=access_token_expires)
    return {"Status": "JWT Generated Successfully", "access_token": access_token, "token_type": "bearer"}



@app.get("/Get_users", status_code=status.HTTP_200_OK, response_model=UserListResponse)
async def get_users(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1), db: Session = Depends(get_db)):
    users, total_users = crud.get_users(db=db, skip=(page - 1) * per_page, limit=per_page)
   
    if total_users == 0:
        return UserListResponse(message="No users found")
 
    next_page_token = None
    if (page * per_page) < total_users:
        next_page_data = {
            "page": page + 1,
            "per_page": per_page,
        }
        next_page_token = jwt.encode(next_page_data, "secret", algorithm="HS256")
       
    return UserListResponse(
        message="Users retrieved successfully",
        page=page,
        users=[crud.user_to_dict(user) for user in users],
        next_page_token=next_page_token
    )

@app.put("/Update/{user_id}", response_model=schemas.User)
async def update_user(user_id: int, user_data: schemas.UserUpdate, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = crud.update_user(db, user_id=user_id, user_data=user_data)
    return updated_user

@app.delete("/Delete/{user_id}")
async def delete_user(user_id: int, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    crud.delete_user(db, user_id)
    return {"message": "User deleted successfully"}
