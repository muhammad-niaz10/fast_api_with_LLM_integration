from pydantic import BaseModel,EmailStr
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    name : str 
    email: EmailStr
    password: str 

class UserResponse(BaseModel):
    id:UUID
    name:str
    email:EmailStr
    is_active:bool 
    created_at:datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email:EmailStr
    password:str