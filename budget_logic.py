import pandas as pd
from datetime import datetime, timedelta
import calendar

# Hardcoded fallback limit
TOTAL_BUDGET = 1000

def normalize_currency(amount: float, currency: str) -> float:
    """
    Converts input amount to EUR using fixed rates.
    """
    rates = {
        "EUR": 1.0,
        "CZK": 0.040, # Updated rate
        "PLN": 0.23,
        "GBP": 1.17,
        "USD": 0.92,
        "MXN": 0.054, # Approx rate
        "HUF": 0.0026
    }
    return round(amount * rates.get(currency, 1.0), 2)

def calculate_burn_rate(df: pd.DataFrame, limit: float = TOTAL_BUDGET) -> dict:
    """
    Calculates the burn rate status for the current month.
    """
    today = datetime.today()
    
    # Filter for current month
    if not df.empty and 'Date' in df.columns:
        # Ensure datetime
        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
             
        current_month_df = df[
            (df['Date'].dt.month == today.month) & 
            (df['Date'].dt.year == today.year)
        ]
        total_spent = current_month_df['Amount_EUR'].sum()
    else:
        total_spent = 0.0

    remaining = limit - total_spent
    
    # Days logic
    _, days_in_month = calendar.monthrange(today.year, today.month)
    days_passed = today.day
    days_left = days_in_month - days_passed
    
    # "Safe" daily spend to last the month
    daily_limit = remaining / days_left if days_left > 0 else 0
    
    # Check status
    status = "OK"
    if remaining < 0:
        status = "CRITICAL"
    elif remaining < (limit * 0.1): # Less than 10% left
        status = "WARNING"
        
    return {
        "total_spent": round(total_spent, 2),
        "remaining": round(remaining, 2),
        "days_left": days_left,
        "daily_limit": round(daily_limit, 2),
        "status": status,
        "percent_used": min(100, round((total_spent / limit) * 100)) if limit > 0 else 0
    }

def check_category_limits(df: pd.DataFrame, rules_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compares spending against category limits.
    """
    if df.empty or rules_df.empty:
        return pd.DataFrame()

    today = datetime.today()
    # Filter current month
    current_month_df = df[
        (df['Date'].dt.month == today.month) & 
        (df['Date'].dt.year == today.year)
    ]
    
    # Group by category
    category_spend = current_month_df.groupby("Category")["Amount_EUR"].sum().reset_index()
    
    # Merge with rules
    merged = pd.merge(rules_df, category_spend, on="Category", how="left")
    merged["Amount_EUR"] = merged["Amount_EUR"].fillna(0)
    merged["Remaining"] = merged["Monthly_Limit"] - merged["Amount_EUR"]
    merged["Status"] = merged.apply(lambda x: "Exceeded" if x["Remaining"] < 0 else "OK", axis=1)
    
    return merged
