import os
import json
import gspread
from google.oauth2 import service_account

# Path to credential file
GCREDS_PATH = os.path.join(os.path.dirname(__file__), "..", ".streamlit", "gcred.json")

# Load creds
with open(GCREDS_PATH) as f:
    creds_dict = json.load(f)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = service_account.Credentials.from_service_account_info(
    creds_dict, scopes=SCOPES
)

gc = gspread.authorize(credentials)

def get_worksheet(sheet_url, worksheet_name):
    sh = gc.open_by_url(sheet_url)
    return sh.worksheet(worksheet_name)

