from src.core.security import get_password_hash

def create_password_hash(password: str):
    return get_password_hash(password)

if __name__ == "__main__":
    password = "user123"  # Password for the non-admin user
    hashed = create_password_hash(password)
    print(f"Hashed password: {hashed}")
