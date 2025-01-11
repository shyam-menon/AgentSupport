import streamlit as st

def show_login():
    """Display login form and handle authentication"""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user" not in st.session_state:
        st.session_state.user = None
        
    if st.session_state.access_token:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Logged in as: {st.session_state.user.get('email')}")
        with col2:
            if st.button("Logout"):
                st.session_state.access_token = None
                st.session_state.user = None
                st.rerun()
    else:
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not email or not password:
                    st.error("Please enter both email and password")
                    return
                    
                # Attempt login
                response = st.session_state.api_client.login(email, password)
                if response and "access_token" in response:
                    st.session_state.access_token = response["access_token"]
                    st.session_state.user = response["user"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid email or password")
