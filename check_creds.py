import gspread
from google.oauth2.service_account import Credentials
import sys

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def check_creds():
    print("Checking credentials...")
    try:
        creds = Credentials.from_service_account_file(
            ".streamlit/credentials.json", scopes=SCOPES
        )
        client = gspread.authorize(creds)
        print("SUCCESS: Credentials are valid and client is authorized.")
        
        # Try to open the sheet (optional, but good to check permissions)
        try:
            # We don't know the exact name the user gave, but we can list available sheets
            # or just print success regarding auth.
            print("Attempting to list spreadsheet files accessible to this service account...")
            files = client.list_spreadsheet_files()
            print(f"Found {len(files)} spreadsheets.")
            for f in files[:3]:
                 print(f" - {f['name']} (ID: {f['id']})")
                 
            if not files:
                print("WARNING: No spreadsheets found. Make sure you shared the sheet with the service account email.")
                
        except Exception as e:
            print(f"Authorized, but failed to list sheets: {e}")

    except Exception as e:
        print(f"ERROR: Failed to authorize. {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_creds()
