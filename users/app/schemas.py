from pydantic import BaseModel
from typing import Optional, List, Dict
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: str
    password: str
class Question(BaseModel):
    question: str
 
class User(BaseModel):
    id: int
    firstname: str
    lastname: str
    email: str

    class Config:
        orm_mode = True
        from_attributes = True

class UserUpdate(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]
    email: Optional[str]  
    
class UserListResponse(BaseModel):
    message: str
    page: int
    users: List[User]
    next_page_token: Optional[str]
