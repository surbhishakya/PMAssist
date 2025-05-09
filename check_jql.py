from jira import JIRA
from dotenv import load_dotenv
import os
import sys
import time

# Load credentials
load_dotenv()

# Initialize JIRA connection with timeout
JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")

jira = JIRA(server=JIRA_URL, token_auth=(JIRA_TOKEN), timeout=30)

# Define and execute JQL query with pagination
JQL = 'project = PGP AND status not in (Queue) ORDER BY updated DESC'
start_at = 0
max_results = 100
max_total_issues = 500  # Limit total issues to prevent timeout
all_issues = []

print("Fetching issues...")
sys.stdout.flush()

try:
    while len(all_issues) < max_total_issues:
        issues = jira.search_issues(
            JQL, 
            startAt=start_at, 
            maxResults=max_results,
            fields='summary,status,assignee,created,updated'  # Only fetch needed fields
        )
        if not issues:
            break
        all_issues.extend(issues)
        start_at += len(issues)
        print(f"Fetched {len(all_issues)} issues so far...", end='\r')
        sys.stdout.flush()
        if len(issues) < max_results:
            break
        time.sleep(0.5)  # Add small delay between requests
except Exception as e:
    print(f"\nError occurred: {str(e)}")

print("\n\nJQL Query Information:")
print(f"Query: {JQL}")
print(f"Total Issues Found: {len(all_issues)}")
print("\nDetailed Results:")
print("-" * 100)

# Print each issue's details
for i, issue in enumerate(all_issues, 1):
    print(f"\nIssue {i}/{len(all_issues)}")
    print(f"Key: {issue.key}")
    print(f"Summary: {issue.fields.summary}")
    print(f"Status: {issue.fields.status.name}")
    print(f"Assignee: {getattr(issue.fields.assignee, 'displayName', 'Unassigned')}")
    print(f"Created: {issue.fields.created[:10]}")
    print(f"Updated: {issue.fields.updated[:10]}")
    print("-" * 100) 