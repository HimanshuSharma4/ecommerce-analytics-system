import pandas as pd
import os
import re

# Configuration Constants
RAW_DIR = '../data/raw'
CLEANED_DIR = '../data/cleaned'

def clean_orders(df_orders):
    """Fixes date formats and handles NULL customer_ids in the orders dataset."""
    print("[INFO] Cleaning orders dataset (Handling NULLs and Date Formats)...")
    initial_count = len(df_orders)
    
    # Handle NULL customer_ids (Dropping to enforce data integrity)
    df_orders = df_orders.dropna(subset=['customer_id']).copy()
    dropped_nulls = initial_count - len(df_orders)
    
    # Normalize date formats to standard 'YYYY-MM-DD HH:MM:SS'
    # 'mixed' format automatically infers standard formats, dayfirst=True helps with DD-MM-YYYY
    df_orders['order_date'] = pd.to_datetime(df_orders['order_date'], format='mixed', dayfirst=True)
    df_orders['order_date'] = df_orders['order_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return df_orders, dropped_nulls

def clean_products(df_products):
    """Normalizes product names by trimming excess whitespaces and applying Title Case."""
    print("[INFO] Cleaning products dataset (Text Normalization)...")
    df_products['product_name'] = df_products['product_name'].astype(str).str.strip().str.title()
    # Replace multiple internal spaces with a single space
    df_products['product_name'] = df_products['product_name'].apply(lambda x: ' '.join(x.split()))
    return df_products

def validate_emails(df_customers):
    """Identifies and returns a list of customer_ids associated with invalid email addresses."""
    print("[INFO] Validating customer emails via Regex pattern...")
    # Standard enterprise Regex for email validation
    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    
    # Filter out emails that do not match the valid pattern
    invalid_mask = ~df_customers['email'].astype(str).apply(lambda x: bool(email_pattern.match(x)))
    invalid_customers = df_customers[invalid_mask]['customer_id'].tolist()
    
    return invalid_customers

def check_referential_integrity(df_order_items, df_orders):
    """Finds item records in order_items that reference non-existent order_ids in the orders table."""
    print("[INFO] Executing Referential Integrity Checks between Orders and Order Items...")
    valid_order_ids = set(df_orders['order_id'])
    invalid_items = df_order_items[~df_order_items['order_id'].isin(valid_order_ids)]
    
    return invalid_items['item_id'].tolist()

def execute_cleaning_pipeline():
    """Main execution function orchestration for the ETL cleaning phase."""
    os.makedirs(CLEANED_DIR, exist_ok=True)
    print("\n[INFO] Initializing Data Cleaning Pipeline...")
    
    # 1. Load Raw Datasets
    try:
        df_customers = pd.read_csv(f'{RAW_DIR}/customers.csv')
        df_products = pd.read_csv(f'{RAW_DIR}/products.csv')
        df_orders = pd.read_csv(f'{RAW_DIR}/orders.csv')
        df_order_items = pd.read_csv(f'{RAW_DIR}/order_items.csv')
    except FileNotFoundError as e:
        print(f"[ERROR] Failed to load raw datasets. Ensure data generation step is completed. Error: {e}")
        return

    # 2. Execute Data Cleaning & Validation Functions
    df_orders_clean, dropped_orders_count = clean_orders(df_orders)
    df_products_clean = clean_products(df_products)
    
    invalid_emails_list = validate_emails(df_customers)
    invalid_item_refs = check_referential_integrity(df_order_items, df_orders_clean)
    
    # Address Negative Quantities in Order Items (Converting to absolute values to fix structural errors)
    df_order_items_clean = df_order_items.copy()
    df_order_items_clean['quantity'] = df_order_items_clean['quantity'].abs()

    # 3. Export Cleaned Datasets
    print("[INFO] Exporting cleaned data assets to designated directory...")
    df_customers.to_csv(f'{CLEANED_DIR}/customers.csv', index=False)
    df_products_clean.to_csv(f'{CLEANED_DIR}/products.csv', index=False)
    df_orders_clean.to_csv(f'{CLEANED_DIR}/orders.csv', index=False)
    df_order_items_clean.to_csv(f'{CLEANED_DIR}/order_items.csv', index=False)
    
    print(f"[SUCCESS] Pipeline complete. Clean datasets exported to: {os.path.abspath(CLEANED_DIR)}")
    
    # 4. Generate Professional Issues Report
    print("\n" + "="*50)
    print("📊 DATA VALIDATION & CLEANING REPORT")
    print("="*50)
    print(f"-> Orders dropped due to NULL customer_id      : {dropped_orders_count}")
    print(f"-> Invalid email addresses detected            : {len(invalid_emails_list)}")
    if invalid_emails_list:
        print(f"   [Sample Invalid Customer IDs]               : {invalid_emails_list[:3]}...")
    print(f"-> Order Items with missing Orders (Orphaned)  : {len(invalid_item_refs)}")
    print("="*50 + "\n")

if __name__ == "__main__":
    execute_cleaning_pipeline()