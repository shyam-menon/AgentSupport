from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

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

    @classmethod
    def from_orm(cls, obj):
        # Add logging to track field conversion
        logging.info(f"Converting object to {cls.__name__}: {obj}")
        if hasattr(obj, '__dict__'):
            logging.info(f"Object attributes: {obj.__dict__}")
        instance = super().from_orm(obj)
        logging.info(f"Converted instance: {instance}")
        return instance

class User(UserInDBBase):
    def __str__(self):
        return f"User(email={self.email}, is_active={self.is_active}, is_admin={self.is_admin})"

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        logging.info(f"User.dict() called: {d}")
        return d

class UserInDB(UserInDBBase):
    hashed_password: str
    is_superuser: bool = False
    is_admin: bool = False  # Add is_admin field to match database
    
    def __str__(self):
        return f"UserInDB(email={self.email}, is_active={self.is_active}, is_admin={self.is_admin}, is_superuser={self.is_superuser})"
