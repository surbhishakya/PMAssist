from jira import JIRA
from dotenv import load_dotenv
import os


# Load credentials
load_dotenv()

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

print("JIRA URL:", JIRA_URL)
print("JIRA EMAIL:", JIRA_EMAIL)

try:
    jira = JIRA(server=JIRA_URL, token_auth=(JIRA_TOKEN))
    user = jira.current_user()
    print(f"✅ Connected to Jira as: {user}")
except Exception as e:
    print(f"❌ Failed to connect to Jira: {e}")
