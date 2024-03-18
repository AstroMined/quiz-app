import os
import requests
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
PAT = os.getenv('AZURE_DEVOPS_PAT')
ORGANIZATION = os.getenv('AZURE_DEVOPS_ORG')
PROJECT = os.getenv('AZURE_DEVOPS_PROJECT')
API_VERSION = "7.1-preview.2"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_work_item_types():
    """Performs a GET request to retrieve work item types from Azure DevOps."""
    url = f"https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis/wit/workitemtypes?api-version={API_VERSION}"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {PAT}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        logging.info("Successfully retrieved work item types.")
        return response.json()
    else:
        logging.error(f"Failed to retrieve work item types: HTTP {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    work_item_types = get_work_item_types()
    if work_item_types:
        print(work_item_types)
