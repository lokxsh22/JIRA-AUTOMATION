import os
import requests
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Environment variables
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_ISSUE_KEY = os.getenv("JIRA_ISSUE_KEY")
ATTACHMENT_DOWNLOAD_PATH = os.getenv("ATTACHMENT_DOWNLOAD_PATH") 

@app.post("/")
async def download_attachments():
    if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN, JIRA_ISSUE_KEY]):
        return {"error": "Missing one or more required environment variables."}

    # Ensure the download directory exists
    os.makedirs(ATTACHMENT_DOWNLOAD_PATH, exist_ok=True)

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    issue_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{JIRA_ISSUE_KEY}"

    # Fetch issue data
    issue_resp = requests.get(issue_url, auth=auth)
    if issue_resp.status_code != 200:
        return {"error": f"Failed to fetch issue. Status: {issue_resp.status_code}", "details": issue_resp.text}

    issue_data = issue_resp.json()
    attachments = issue_data["fields"].get("attachment", [])
    results = []

    for attachment in attachments:
        filename = attachment["filename"]
        content_url = attachment["content"]
        full_path = os.path.join(ATTACHMENT_DOWNLOAD_PATH, filename)

        try:
            resp = requests.get(content_url, auth=auth)
            if resp.status_code == 200:
                with open(full_path, "wb") as f:
                    f.write(resp.content)
                results.append(f"Downloaded: {full_path}")
            else:
                results.append(f"Failed to download {filename}: HTTP {resp.status_code}")
        except Exception as e:
            results.append(f"Error downloading {filename}: {str(e)}")

    return {"results": results}
