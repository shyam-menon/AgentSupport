from typing import Optional
from src.core.security import verify_password
from src.schemas.user import User, UserInDB

# In-memory user database for development
users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": "$2b$12$4MGjcGyevRLJQNUOo2b6oOzrToesVyBmVR2/uTJgxUwLMCqzk3CU.",  # "password123"
        "is_active": True,
        "is_superuser": True
    }
}

def get_user_by_email(email: str) -> Optional[UserInDB]:
    """Get user from database by email."""
    if email in users_db:
        user_dict = users_db[email]
        return UserInDB(**user_dict)
    return None

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user by email and password."""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return User(
        email=user.email,
        is_active=user.is_active,
        is_admin=user.is_superuser,  # Map superuser to admin
        full_name=None
    )
