import streamlit as st

def show_home():
    st.title("Support Tool System")
    
    st.write("""
    Welcome to the Support Tool System! This intelligent system helps you find relevant solutions 
    based on historical ticket data.
    
    ### Features:
    - Search through historical support tickets
    - Get AI-powered resolution suggestions
    - View similar cases and their solutions
    - Export search results
    
    ### Getting Started:
    1. Navigate to the Search page using the sidebar
    2. Enter your issue description
    3. Add optional filters like Issue Type and Affected System
    4. Click Search to find relevant solutions
    
    For administrative tasks like data management, please use the Admin section.
    """)
