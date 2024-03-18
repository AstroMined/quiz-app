import os
import json
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()
PAT = os.getenv('AZURE_DEVOPS_PAT')
JSON_DIR = os.getenv('JSON_DIR')
ORGANIZATION = os.getenv('AZURE_DEVOPS_ORG')
PROJECT = os.getenv('AZURE_DEVOPS_PROJECT')
BASE_URL = f"https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis/wit/workitems/$"
API_VERSION = "7.1-preview.2"

# Setup logging
processed_dir = Path(JSON_DIR, "processed")
processed_dir.mkdir(exist_ok=True)
logging.basicConfig(filename=processed_dir / "process_log.log", level=logging.ERROR,
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def read_pat_from_env():
    """Reads the Personal Access Token from .env file."""
    return PAT

def find_json_files(directory, filenames):
    """Finds JSON files in the specified directory matching the given filenames."""
    files = []
    for filename in filenames:
        filepath = Path(directory, filename)
        if filepath.is_file() and os.path.getsize(filepath) > 0:  # Check if file is not empty
            files.append(filepath)
    return files

def create_azure_devops_item(url, payload, headers):
    """Creates an item in Azure DevOps using the specified URL and payload."""
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code not in range(200, 299):
        logging.error(f"Failed to create item: {response.text}")
    return response.json()

def process_json_files(directory, filenames):
    """Processes all JSON files, making API calls to Azure DevOps, and then moves them to the 'processed' directory."""
    pat = read_pat_from_env()
    headers = {"Content-Type": "application/json-patch+json",
               "Authorization": f"Basic {pat}"}

    for filepath in find_json_files(directory, filenames):
        with open(filepath, 'r') as file:
            payload = json.load(file)
        
        item_type = filepath.stem.split('_')[-1]  # Extract item type from filename
        url = f"{BASE_URL}{item_type.capitalize()}?api-version={API_VERSION}"
        create_azure_devops_item(url, payload, headers)

        # Move processed file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        processed_filepath = processed_dir / f"{filepath.stem}_{timestamp}.json"
        filepath.rename(processed_filepath)

        # Recreate blank file
        filepath.touch()

if __name__ == "__main__":
    filenames = ["create_epics_features.json", "create_user_stories.json", "create_tasks.json", "create_bugs_issues.json"]
    try:
        process_json_files(JSON_DIR, filenames)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
