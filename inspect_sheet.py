import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_ID = "1VfJvS8gLQ7lRg2KEnmMPnqZZws9_qHXUPKw1GMRpZxU"

def inspect_sheet():
    print(f"Connecting into sheet ID: {SHEET_ID}...")
    creds = Credentials.from_service_account_file(
        ".streamlit/credentials.json", scopes=SCOPES
    )
    client = gspread.authorize(creds)
    
    try:
        # Try opening by name
        print("Attempting to open by name: 'Personal Finance Tracker'")
        sh = client.open("Personal Finance Tracker")
        print(f"Opened spreadsheet: {sh.title}")
        
        worksheets = sh.worksheets()
        print(f"Found {len(worksheets)} worksheets:")
        
        for ws in worksheets:
            print(f" - '{ws.title}' (ID: {ws.id})")
            headers = ws.row_values(1)
            print(f"   Headers: {headers}")

    except Exception as e:
        print(f"Error inspecting sheet by name: {e}")


if __name__ == "__main__":
    inspect_sheet()
