import os
import sys

# Add the frontend directory to Python path
frontend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, frontend_dir)

from src.app import main

if __name__ == "__main__":
    main()
