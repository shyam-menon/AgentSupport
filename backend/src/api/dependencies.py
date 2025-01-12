from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.core.security import verify_token
from src.services.auth import get_user_by_email
from src.schemas.user import User
from src.db.vector_store import VectorStore
import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_vector_store() -> VectorStore:
    """Get vector store instance"""
    return VectorStore()

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    logging.info("Verifying token")
    token_data = verify_token(token)
    if not token_data:
        logging.error("Token verification failed")
        raise credentials_exception
    
    logging.info(f"Token payload: {token_data}")
    email = token_data.get("sub")
    if not email:
        logging.error("No email in token payload")
        raise credentials_exception
    
    logging.info(f"Getting user by email: {email}")
    user = get_user_by_email(email)
    if not user:
        logging.error(f"User not found: {email}")
        raise credentials_exception
    
    # Get admin status from token
    is_admin = token_data.get("is_admin", False)
    is_superuser = token_data.get("is_superuser", False)
    logging.info(f"Token admin status: is_admin={is_admin}, is_superuser={is_superuser}")
    
    # Create User with admin status from token
    user_data = {
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": is_admin or is_superuser,  # Use admin status from token
        "full_name": user.full_name
    }
    logging.info(f"Creating User object with data: {user_data}")
    return User(**user_data)

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current user and verify they are an admin"""
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
