import data_manager
import budget_logic
import pandas as pd
from datetime import date

def test_integration():
    print("Testing Data Manager...")
    
    # 1. Test Reading Rules
    print("Reading Budget Rules...")
    rules = data_manager.get_budget_rules()
    if not rules.empty:
        print(f"Success. Found {len(rules)} rules.")
        print(rules.head(1))
    else:
        print("Warning: No rules found or connection failed.")

    # 2. Test Adding Transaction
    print("\nTesting Add Transaction...")
    test_date = date.today()
    amount = 50
    currency = "CZK"
    category = "Test"
    desc = "Integration Test"
    amount_eur = budget_logic.normalize_currency(amount, currency)
    
    success = data_manager.add_transaction(
        test_date, amount, currency, category, desc, amount_eur
    )
    
    if success:
        print(f"Success. Added {amount} {currency} ({amount_eur} EUR).")
    else:
        print("Error adding transaction.")
        return

    # 3. Test Reading Transactions
    print("\nReading Transactions...")
    df = data_manager.get_transactions()
    if not df.empty:
        print(f"Success. Found {len(df)} transactions.")
        print(df.tail(1))
        
        # 4. Test Burn Rate Logic
        print("\nTesting Burn Rate Calculation...")
        stats = budget_logic.calculate_burn_rate(df)
        print("Burn Rate Stats:", stats)
    else:
        print("Error: Could not read back the transaction.")

if __name__ == "__main__":
    test_integration()
