import os
import json
import gspread
from google.oauth2 import service_account

# --- Load credentials from environment variable ---
gcred_str = os.getenv("GCRED_JSON")
if not gcred_str:
    raise EnvironmentError("❌ 'GCRED_JSON' environment variable not found.")

# --- Convert to dict & clean private key ---
creds_dict = json.loads(gcred_str)
creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# --- Create credentials ---
credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
gc = gspread.authorize(credentials)

# --- Exported method ---
def get_worksheet(sheet_url, worksheet_name):
    sh = gc.open_by_url(sheet_url)
    return sh.worksheet(worksheet_name)

def update_worksheet_rows(sheet_url, worksheet_name, rows):
    """
    Appends a list of dicts (rows) to the worksheet. Each dict should have keys matching the worksheet's columns.
    """
    ws = get_worksheet(sheet_url, worksheet_name)
    # Get header from the first row
    header = ws.row_values(1)
    to_append = []
    for row in rows:
        # Ensure the order matches the header
        to_append.append([row.get(col, "") for col in header])
    ws.append_rows(to_append, value_input_option="USER_ENTERED")
