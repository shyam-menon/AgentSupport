# Support Tool System

A support ticket analysis system using FastAPI for the backend and Streamlit for the frontend.

## Starting the Application

1. Start the Backend:
```bash
cd backend
venv/Scripts/python -m uvicorn src.main:app --host localhost --port 8080 --log-level info
```

2. Start the Frontend:
```bash
cd frontend
venv/Scripts/streamlit run run_app.py
```

The application will be available at:
- Frontend: http://localhost:8501
- Backend: http://localhost:8080

## Default Login Credentials

For development purposes, use these credentials:
- Username: admin@example.com
- Password: password123

## Authentication

The system supports two types of users:

### 1. Admin User
- Email: admin@example.com
- Password: password123
- Permissions:
  - Access to Home and Search pages
  - Access to Admin dashboard
  - Can upload and process CSV files
  - Can view system statistics

### 2. Regular User
- Email: user@example.com
- Password: user123
- Permissions:
  - Access to Home and Search pages
  - Cannot access Admin dashboard

### Features by Role

#### Admin Features
- Full access to search functionality
- Upload CSV files for processing
- Convert CSV data to markdown format
- Generate embeddings using Azure OpenAI
- View system statistics
- Manage ticket data

#### Regular User Features
- Search through existing tickets
- View similar cases and solutions
- Access historical support data

### Security
- JWT-based authentication
- Role-based access control
- Secure password hashing using bcrypt
- Token expiration and refresh

## Configuration

### Backend Configuration
- Runs on port 8080
- Environment variables in `.env`:
  ```
  # Azure OpenAI Configuration
  AZURE_OPENAI_API_KEY=your_api_key
  AZURE_OPENAI_ENDPOINT=your_endpoint
  AZURE_OPENAI_API_VERSION=2023-05-15

  # Security
  SECRET_KEY=your_secret_key
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30

  # CORS
  BACKEND_CORS_ORIGINS=["http://localhost:8501"]
  ```

### Frontend Configuration
- Runs on port 8501
- Environment variables in `.env`:
  ```
  BACKEND_URL=http://localhost:8080
  STREAMLIT_SERVER_ADDRESS=localhost
  ```
- Streamlit config in `.streamlit/config.toml`:
  ```
  [server]
  port = 8501
  address = "localhost"
  headless = true

  [logger]
  level = "debug"

  [browser]
  gatherUsageStats = false
  ```

## Prerequisites

- Python 3.10 or higher
- Azure OpenAI API access (for embeddings)
- Required Python packages:
  - Backend: FastAPI, Uvicorn, python-jose[cryptography], passlib[bcrypt], python-multipart
  - Frontend: Streamlit, requests, python-dotenv

## Setup Instructions

### 1. Clone the repository
```bash
git clone <repository-url>
cd AgentSupport
```

### 2. Create virtual environments
```bash
# Windows
python -m venv backend\venv
python -m venv frontend\venv
```

### 3. Install dependencies
```bash
# Backend (Windows)
backend\venv\Scripts\activate
pip install -r backend\requirements.txt
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
deactivate

# Frontend (Windows)
frontend\venv\Scripts\activate
pip install -r frontend\requirements.txt
deactivate
```

### 4. Configure environment variables
1. Create `backend/.env` and `frontend/.env` using the configuration examples above
2. Update the Azure OpenAI credentials in `backend/.env`
3. Generate a secure random string for `SECRET_KEY` in `backend/.env`

### 5. Activating Virtual Environments

#### For Backend:
```bash
# Navigate to backend directory
cd backend

# Activate the virtual environment
.\venv\Scripts\activate

# Your prompt should now show (venv) indicating the environment is active
# Run the backend server
python -m uvicorn src.main:app --host localhost --port 8080 --log-level info

#Run with additional logs
python -m uvicorn src.main:app --host localhost --port 8080 --reload
```

#### For Frontend:
```bash
# Navigate to frontend directory
cd frontend

# Activate the virtual environment
.\venv\Scripts\activate

# Your prompt should now show (venv) indicating the environment is active
# Run the frontend application
streamlit run run_app.py
streamlit run run_app.py --logger.level=info
```

To deactivate the virtual environment when you're done:
```bash
deactivate
```

Note: Always ensure you're running commands from a terminal with the appropriate virtual environment activated. The terminal prompt should show `(venv)` when the virtual environment is active.

## Project Structure

```
AgentSupport/
├── backend/                # FastAPI backend service
│   ├── src/
│   │   ├── api/           # API routes and dependencies
│   │   ├── core/          # Core configurations
│   │   ├── db/            # Database and vector store
│   │   ├── schemas/       # Pydantic models
│   │   └── services/      # Business logic
│   └── requirements.txt
│
├── frontend/              # Streamlit web application
│   ├── src/
│   │   ├── pages/        # Streamlit pages
│   │   ├── components/   # Reusable UI components
│   │   └── utils/        # Utility functions
│   └── requirements.txt
│
└── README.md
```

## Troubleshooting

### Authentication Issues
- Ensure both backend and frontend are running on the correct ports (8080 and 8501)
- Check that `BACKEND_URL` in frontend's `.env` points to the correct backend URL
- Verify that `BACKEND_CORS_ORIGINS` in backend's `.env` includes the frontend URL
- Make sure all required authentication packages are installed in the backend

### Connection Issues
- Check if the ports are not in use by other applications
- Try using `localhost` instead of `127.0.0.1` in configuration files
- Ensure Windows Defender Firewall is not blocking the connections

### Startup Issues
- Use `--log-level debug` with uvicorn to see detailed backend logs
- Use `--logger.level=debug` with streamlit to see detailed frontend logs
- Check that all required Python packages are installed in both environments
