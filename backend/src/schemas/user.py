from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserInDBBase(UserBase):
    class Config:
        from_attributes = True

class User(UserInDBBase):
    def __str__(self):
        return f"User(email={self.email}, is_active={self.is_active}, is_admin={self.is_admin})"

class UserInDB(UserInDBBase):
    hashed_password: str
    is_superuser: bool = False
    
    def __str__(self):
        return f"UserInDB(email={self.email}, is_active={self.is_active}, is_superuser={self.is_superuser})"
