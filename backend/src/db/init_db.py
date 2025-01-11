from src.db.base import Base, engine
from src.db.models.user import User
from src.core.security import get_password_hash
from sqlalchemy.orm import Session
from src.db.base import SessionLocal

def init_db() -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Check if we already have the admin user
        user = db.query(User).filter(User.email == "admin@example.com").first()
        if not user:
            # Create default admin user
            admin_user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("password123"),
                full_name="Admin User",
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            print("Created default admin user")
        else:
            print("Admin user already exists")
            
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial data")
    init_db()
    print("Initial data created")
