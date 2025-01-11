from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from src.core.security import create_access_token
from src.core.config import settings
from src.services.auth import authenticate_user, get_user_by_email
from src.schemas.user import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")  

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"Login attempt - username: {form_data.username}")
    
    # First check if user exists
    user_db = get_user_by_email(form_data.username)
    print(f"User found in DB: {user_db is not None}")
    if user_db:
        print(f"User details: {user_db}")
    
    # Try to authenticate
    user = authenticate_user(form_data.username, form_data.password)
    print(f"Authentication result: {user is not None}")
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Convert user to dict for response
    user_data = {
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "full_name": user.full_name
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }
