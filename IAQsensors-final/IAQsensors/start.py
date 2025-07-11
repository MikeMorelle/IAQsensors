import streamlit as st

# Define username and password (for demo purposes)
USERNAME = 'admin'
PASSWORD = 'password123'

# Function to check credentials
def check_credentials(username, password):
    return username == USERNAME and password == PASSWORD

# Login page UI
def login_page():
    st.title("Login Page")

    # Username and password inputs
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    # Button for login
    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.logged_in = True  # Store login status
            st.success("Login successful!")
            st.experimental_rerun()  # Rerun the app to show the main pages
        else:
            st.error("Invalid username or password")

# Show the main pages after login
def show_main_pages():
    # Sidebar navigation for different pages
    page = st.sidebar.selectbox("Select a page", ["Home", "IAQ Charts", "IAQ Dashboard", "System Health"])

    if page == "Home":
        show_home()
    elif page == "IAQ Charts":
        show_iaq_charts()
    elif page == "IAQ Dashboard":
        show_iaq_dashboard()
    elif page == "System Health":
        show_system_health()

# Home page content
def show_home():
    st.title("Real-Time Indoor Air Quality Monitoring")
    st.subheader("Scope")
    st.markdown("""
    "The quality of the air we breathe has a profound impact on human health, perceived wellbeing, and performance."
    """)
    st.markdown("""
    - Schools and universities
    - Offices and workplaces
    - Residential buildings
    """)

# IAQ Charts page content
def show_iaq_charts():
    st.title("IAQ Charts")
    st.write("Display your IAQ charts and graphs here.")

# IAQ Dashboard page content
def show_iaq_dashboard():
    st.title("IAQ Dashboard")
    st.write("Display your IAQ Dashboard here.")

# System Health page content
def show_system_health():
    st.title("System Health")
    st.write("Display system health information here.")

# Main app logic
def main():
    # Check if user is logged in, if not show login page
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()  # Show login page if the user is not logged in
    else:
        # Sidebar navigation only available after login
        st.sidebar.title("Navigation")
        show_main_pages()  # Show main pages if the user is logged in

# Run the app
if __name__ == "__main__":
    main()
