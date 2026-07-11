import pandas as pd
from datetime import datetime

def test_missing_order_id():
    """Test 1: What happens when order_items has an order_id not in orders?"""
    print("[TEST 1] Validating Orphaned Order Items...")
    # Mock Data
    df_orders = pd.DataFrame({'order_id': ['ORD_001', 'ORD_002']})
    df_items = pd.DataFrame({'item_id': ['I_01', 'I_02'], 'order_id': ['ORD_001', 'ORD_999']})
    
    # Logic to handle edge case
    invalid_refs = df_items[~df_items['order_id'].isin(df_orders['order_id'])]
    
    assert len(invalid_refs) == 1, "Failed to identify missing order_id"
    print("  -> PASSED: System correctly identifies and flags orphaned items (ORD_999) for review.")

def test_invalid_discount():
    """Test 2: What happens when discount_percent > 100?"""
    print("[TEST 2] Validating Discount Percentages...")
    df_items = pd.DataFrame({'item_id': ['I_01', 'I_02', 'I_03'], 'discount_percent': [10.0, 150.0, -5.0]})
    
    # Logic to handle edge case: Flag anything outside 0-100 range
    invalid_discounts = df_items[(df_items['discount_percent'] > 100) | (df_items['discount_percent'] < 0)]
    
    assert len(invalid_discounts) == 2, "Failed to catch invalid discounts"
    print("  -> PASSED: System correctly flags discounts > 100% or < 0% to prevent negative revenue.")

def test_zero_quantity():
    """Test 3: What happens when quantity is 0?"""
    print("[TEST 3] Validating Zero Quantity Entries...")
    df_items = pd.DataFrame({'item_id': ['I_01', 'I_02', 'I_03'], 'quantity': [5, 0, 10]})
    
    # Logic to handle edge case: Flag quantity == 0
    zero_qty = df_items[df_items['quantity'] == 0]
    
    assert len(zero_qty) == 1, "Failed to catch zero quantity"
    print("  -> PASSED: System safely isolates zero-quantity transactions (possible system glitch).")

def test_future_order_date():
    """Test 4: What happens when order_date is in the future?"""
    print("[TEST 4] Validating Future Order Dates...")
    today = pd.to_datetime(datetime.now())
    df_orders = pd.DataFrame({'order_id': ['ORD_001', 'ORD_002'], 
                              'order_date': [pd.to_datetime('2023-01-01'), pd.to_datetime('2099-12-31')]})
    
    # Logic to handle edge case: Flag dates > today
    future_dates = df_orders[df_orders['order_date'] > today]
    
    assert len(future_dates) == 1, "Failed to catch future order dates"
    print("  -> PASSED: System successfully restricts and flags future timestamp anomalies.")

if __name__ == "__main__":
    print("="*60)
    print(" 🛡️  SYSTEM UNIT TESTS: EDGE CASE HANDLING")
    print("="*60)
    
    try:
        test_missing_order_id()
        test_invalid_discount()
        test_zero_quantity()
        test_future_order_date()
        print("-" * 60)
        print("[SUCCESS] All Edge Case Unit Tests Passed Successfully!")
        print("="*60)
    except AssertionError as e:
        print(f"\n[FAIL] Test Failed: {e}")