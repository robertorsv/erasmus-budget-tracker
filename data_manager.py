import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SHEET_NAME = "Personal Finance Tracker"

@st.cache_resource
def get_client():
    """
    Connects to Google Sheets using credentials.
    """
    try:
        # Check if authenticating via secrets (Cloud) or local file
        # We try-except checking st.secrets because accessing it outside streamlit might be tricky
        try:
            if "gcp_service_account" in st.secrets:
                creds = Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"], scopes=SCOPES
                )
                return gspread.authorize(creds)
        except (FileNotFoundError, AttributeError):
            pass # Fallback to local file

        # Local development
        creds = Credentials.from_service_account_file(
            ".streamlit/credentials.json", scopes=SCOPES
        )
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Connection Error: {e}") # Print to console for debugging
        # st.error(f"Failed to connect to Google Sheets: {e}")
        return None


def get_transactions() -> pd.DataFrame:
    """
    Fetches all transactions.
    """
    client = get_client()
    if not client: return pd.DataFrame()
    
    try:
        sh = client.open(SHEET_NAME)
        ws = sh.worksheet("Transactions")
        data = ws.get_all_records()
        df = pd.DataFrame(data)
        
        # Ensure correct types
        if not df.empty:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
            df['Amount_EUR'] = pd.to_numeric(df['Amount_EUR'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error reading transactions: {e}")
        return pd.DataFrame()

def get_budget_rules() -> pd.DataFrame:
    """
    Fetches budget rules.
    """
    client = get_client()
    if not client: return pd.DataFrame()
    
    try:
        sh = client.open(SHEET_NAME)
        ws = sh.worksheet("Budget_Rules")
        data = ws.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error reading budget rules: {e}")
        return pd.DataFrame()

def add_transaction(date, amount, currency, category, desc, amount_eur):
    """
    Appends a new transaction row.
    """
    client = get_client()
    if not client: return False
    
    try:
        sh = client.open(SHEET_NAME)
        ws = sh.worksheet("Transactions")
        
        # Row format: [Date, Amount, Currency, Category, Description, Amount_EUR]
        row = [
            str(date), 
            float(amount), 
            currency, 
            category, 
            desc, 
            float(amount_eur)
        ]
        ws.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error saving transaction: {e}")
        return False
