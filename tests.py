import unittest
import pandas as pd
from budget_logic import calculate_burn_rate, normalize_currency, check_category_limits, TOTAL_BUDGET

class TestBudgetLogic(unittest.TestCase):

    def test_currency_normalization(self):
        # EUR to EUR
        self.assertEqual(normalize_currency(100, "EUR"), 100.0)
        # CZK to EUR (Rate: 0.040)
        self.assertEqual(normalize_currency(1000, "CZK"), 40.0)
        # Unknown currency fallback
        self.assertEqual(normalize_currency(50, "XYZ"), 50.0)

    def test_burn_rate_calculation(self):
        # Mock dataframe
        data = {
            "Date": [pd.Timestamp.today()],
            "Amount_EUR": [500.0]
        }
        df = pd.DataFrame(data)
        
        # Test 50% usage
        stats = calculate_burn_rate(df, limit=1000)
        self.assertEqual(stats['total_spent'], 500.0)
        self.assertEqual(stats['remaining'], 500.0)
        self.assertEqual(stats['percent_used'], 50)
        self.assertEqual(stats['status'], "OK")

    def test_budget_breach(self):
        # Mock dataframe with breach
        data = {
            "Date": [pd.Timestamp.today()],
            "Amount_EUR": [1100.0]
        }
        df = pd.DataFrame(data)
        
        stats = calculate_burn_rate(df, limit=1000)
        self.assertEqual(stats['status'], "CRITICAL")
        self.assertEqual(stats['remaining'], -100.0)

    def test_category_limits(self):
        # Transactions
        trans_data = {
            "Date": [pd.Timestamp.today(), pd.Timestamp.today()],
            "Category": ["Food", "Food"],
            "Amount_EUR": [100.0, 250.0] # Total 350
        }
        df = pd.DataFrame(trans_data)
        
        # Rules
        rules_data = {
            "Category": ["Food"],
            "Monthly_Limit": [300]
        }
        rules_df = pd.DataFrame(rules_data)
        
        result = check_category_limits(df, rules_df)
        
        # Check if Food is exceeded
        food_status = result[result["Category"] == "Food"].iloc[0]
        self.assertEqual(food_status["Amount_EUR"], 350.0)
        self.assertTrue(food_status["Remaining"] < 0)
        self.assertEqual(food_status["Status"], "Exceeded")

if __name__ == '__main__':
    unittest.main()
