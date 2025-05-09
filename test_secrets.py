import streamlit as st
import requests
from jira import JIRA

# Test JIRA Configuration
st.title("Testing Secrets Configuration")

# Test JIRA Secrets
st.header("Testing JIRA Secrets")
try:
    # Get JIRA credentials
    JIRA_URL = st.secrets["JIRA"]["url"]
    JIRA_EMAIL = st.secrets["JIRA"]["email"]
    JIRA_TOKEN = st.secrets["JIRA"]["token"]
    
    st.write("✅ JIRA Secrets loaded successfully")
    st.write(f"URL: {JIRA_URL}")
    st.write(f"Email: {JIRA_EMAIL}")
    st.write("Token: [Hidden for security]")
    
    # Test JIRA URL accessibility
    st.write("\nTesting JIRA URL accessibility...")
    try:
        response = requests.get(JIRA_URL, timeout=5)
        st.write(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            st.success("✅ JIRA URL is accessible")
        else:
            st.error(f"❌ JIRA URL returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Cannot access JIRA URL: {str(e)}")
    
    # Test JIRA Authentication
    st.write("\nTesting JIRA Authentication...")
    try:
        jira = JIRA(
            server=JIRA_URL,
            basic_auth=(JIRA_EMAIL, JIRA_TOKEN),
            validate=True
        )
        user = jira.current_user()
        st.success(f"✅ Successfully authenticated as: {user}")
    except Exception as e:
        st.error(f"❌ JIRA Authentication failed: {str(e)}")
        
except Exception as e:
    st.error(f"❌ Failed to load JIRA secrets: {str(e)}")

# Test SMTP Configuration
st.header("Testing SMTP Secrets")
try:
    # Get SMTP credentials
    SMTP_SERVER = st.secrets["SMTP"]["server"]
    SMTP_PORT = st.secrets["SMTP"]["port"]
    SMTP_USERNAME = st.secrets["SMTP"]["username"]
    SMTP_PASSWORD = st.secrets["SMTP"]["password"]
    SENDER_EMAIL = st.secrets["SMTP"]["sender_email"]
    
    st.write("✅ SMTP Secrets loaded successfully")
    st.write(f"Server: {SMTP_SERVER}")
    st.write(f"Port: {SMTP_PORT}")
    st.write(f"Username: {SMTP_USERNAME}")
    st.write(f"Sender Email: {SENDER_EMAIL}")
    st.write("Password: [Hidden for security]")
    
except Exception as e:
    st.error(f"❌ Failed to load SMTP secrets: {str(e)}") 