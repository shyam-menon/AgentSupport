import streamlit as st

def show_login():
    """Display login form and handle authentication"""
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
    if "user" not in st.session_state:
        st.session_state.user = None
        
    if st.session_state.access_token:
        st.write(f"Logged in as:")
        st.markdown(f"[{st.session_state.user.get('email')}](mailto:{st.session_state.user.get('email')})")
        if st.button("Logout", key="logout_button", use_container_width=True):
            # Clear all session state
            st.session_state.access_token = None
            st.session_state.user = None
            st.session_state.api_client.token = None
            st.rerun()
    else:
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
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
