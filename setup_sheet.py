import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "Personal Finance Tracker"

def setup_sheet():
    print(f"Connecting to '{SHEET_NAME}'...")
    creds = Credentials.from_service_account_file(
        ".streamlit/credentials.json", scopes=SCOPES
    )
    client = gspread.authorize(creds)
    
    try:
        sh = client.open(SHEET_NAME)
        
        # 1. Setup Transactions Tab
        try:
            ws_trans = sh.worksheet("Transactions")
            print("Transactions tab exists.")
        except gspread.WorksheetNotFound:
            print("Creating Transactions tab...")
            # Check if Sheet1 exists and is empty, rename it
            try:
                ws_default = sh.worksheet("Sheet1")
                if not ws_default.get_all_values():
                    ws_default.update_title("Transactions")
                    ws_trans = ws_default
                    print("Renamed Sheet1 to Transactions.")
                else:
                    ws_trans = sh.add_worksheet("Transactions", rows=1000, cols=10)
            except gspread.WorksheetNotFound:
                 ws_trans = sh.add_worksheet("Transactions", rows=1000, cols=10)

        # Update Headers for Transactions
        headers_trans = ["Date", "Amount", "Currency", "Category", "Description", "Amount_EUR"]
        current_headers = ws_trans.row_values(1)
        if not current_headers:
            ws_trans.update(range_name="A1:F1", values=[headers_trans])
            print("Added headers to Transactions.")
        
        # 2. Setup Budget_Rules Tab
        try:
            ws_rules = sh.worksheet("Budget_Rules")
            print("Budget_Rules tab exists.")
        except gspread.WorksheetNotFound:
            print("Creating Budget_Rules tab...")
            ws_rules = sh.add_worksheet("Budget_Rules", rows=100, cols=5)
        
        # Update Headers for Budget_Rules
        headers_rules = ["Category", "Monthly_Limit", "Alert_Threshold"]
        current_headers_rules = ws_rules.row_values(1)
        if not current_headers_rules:
            ws_rules.update(range_name="A1:C1", values=[headers_rules])
            print("Added headers to Budget_Rules.")
            
            # Add Default Rules
            default_rules = [
                ["Rent", 400, 380],
                ["Food", 300, 270],
                ["Travel", 200, 180],
                ["Fun", 100, 90],
                ["Other", 50, 45]
            ]
            ws_rules.update(range_name="A2:C6", values=default_rules)
            print("Added default budget rules.")

        print("Sheet setup complete.")

    except Exception as e:
        print(f"Error setting up sheet: {e}")

if __name__ == "__main__":
    setup_sheet()
