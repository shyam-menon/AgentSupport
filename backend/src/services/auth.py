from typing import Optional
import logging
from src.core.security import verify_password
from src.schemas.user import User, UserInDB

# In-memory user database for development
users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": "$2b$12$4MGjcGyevRLJQNUOo2b6oOzrToesVyBmVR2/uTJgxUwLMCqzk3CU.",  # "password123"
        "is_active": True,
        "is_superuser": True,
        "is_admin": True,  # Add is_admin field
        "full_name": "Admin User"
    },
    "user@example.com": {
        "email": "user@example.com",
        "hashed_password": "$2b$12$9Rzp.2Zszdv2pdOq6jveGeoGW28URcVs7Rwf6uaA6VB7ewbKzqh1S",  # "user123"
        "is_active": True,
        "is_superuser": False,
        "is_admin": False,  # Add is_admin field
        "full_name": "Regular User"
    }
}

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user from database by email."""
    logging.info(f"Fetching user from database: {email}")
    if email in users_db:
        user_dict = users_db[email].copy()  # Make a copy to avoid modifying the original
        # Ensure is_admin is set based on is_superuser for backward compatibility
        user_dict["is_admin"] = user_dict.get("is_admin", user_dict["is_superuser"])
        logging.info(f"Found user in database: {user_dict}")
        user = UserInDB(**user_dict)
        logging.info(f"Created UserInDB object: {user}")
        return user
    logging.warning(f"User not found in database: {email}")
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user by email and password."""
    logging.info(f"Authenticating user: {email}")
    user = get_user_by_email(email)
    if not user:
        logging.error(f"Authentication failed: User not found: {email}")
        return None
    if not verify_password(password, user.hashed_password):
        logging.error(f"Authentication failed: Invalid password for user: {email}")
        return None
        
    # Create User object from UserInDB
    user_data = {
        "email": user.email,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "full_name": user.full_name
    }
    return User(**user_data)
