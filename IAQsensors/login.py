import streamlit as st

st.set_page_config(page_title="Login Page", layout="wide")
st.title("IMQ Monitoring System Login")

# Initialize login state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit_button = st.form_submit_button("Login")

    if submit_button:
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login Successful!")
            
            # Add slight delay to show success message
            import time
            time.sleep(1)
            
            # Correct redirect path
            st.switch_page("./pages/IAQ Dashboard.py")  # Note: "./pages/" prefix
        else:
            st.error("Invalid credentials")