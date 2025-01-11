from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.core.security import verify_token
from src.services.auth import get_user_by_email
from src.schemas.user import User
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logging.info("Verifying token")
    payload = verify_token(token)
    if payload is None:
        logging.error("Token verification failed")
        raise credentials_exception
    
    logging.info(f"Token payload: {payload}")
    email: str = payload.get("sub")
    if email is None:
        logging.error("No email in token payload")
        raise credentials_exception
    
    # Get admin status from token
    is_admin = payload.get("is_admin", False)
    is_superuser = payload.get("is_superuser", False)
    logging.info(f"Token admin status: is_admin={is_admin}, is_superuser={is_superuser}")
    
    logging.info(f"Getting user by email: {email}")
    user = get_user_by_email(email)
    if user is None:
        logging.error(f"User not found: {email}")
        raise credentials_exception
    
    # Create User with admin status from token
    user_data = {
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": is_admin or is_superuser,  # Use admin status from token
        "full_name": user.full_name
    }
    logging.info(f"Creating User object with data: {user_data}")
    return User(**user_data)

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    logging.info(f"Checking admin access for user: {current_user}")
    logging.info(f"User admin status: {current_user.is_admin}")
    logging.info(f"User dict: {current_user.dict()}")
    
    if not current_user.is_admin:
        logging.error(f"Access denied: User {current_user.email} is not an admin (is_admin={current_user.is_admin})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have admin privileges"
        )
    logging.info(f"Admin access granted for user: {current_user.email}")
    return current_user
