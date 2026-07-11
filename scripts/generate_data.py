import pandas as pd
import numpy as np
from faker import Faker
import random
import os

# Initialize Faker with seed for dataset reproducibility
fake = Faker('en_IN')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# Configuration Constants
NUM_RECORDS = 500
OUTPUT_DIR = '../data/raw'
REGION_CODES = ['DL', 'MH', 'KA', 'UP', 'TN', 'HR', 'GJ', 'WB', 'TS', 'KA']

def generate_raw_data():
    """
    Generates synthetic enterprise e-commerce datasets with intentional anomalies 
    to validate down-stream ETL pipelines and data cleaning functions.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("[INFO] Initializing e-commerce data generation pipeline...")

    # ==========================================
    # 1. Customers Dataset Generation
    # ==========================================
    print("[INFO] Processing customers dataset...")
    customers = []
    customer_types = ['REGULAR', 'PREMIUM', 'VIP']
    
    for i in range(1, NUM_RECORDS + 1):
        email = fake.email()
        # Anomaly Injection: 2% invalid email formats (structural errors)
        if random.random() < 0.02: 
            email = email.replace('@', '') if random.choice([True, False]) else email.split('@')[0]
            
        customers.append({
            'customer_id': f"CUST_{i:04d}", 
            'customer_name': fake.name(), 
            'email': email, 
            'registration_date': fake.date_time_between(start_date='-2y', end_date='now').strftime('%Y-%m-%d %H:%M:%S'), 
            'customer_type': random.choice(customer_types)
        })
        
    df_customers = pd.DataFrame(customers)
    df_customers.to_csv(f'{OUTPUT_DIR}/customers.csv', index=False)
    print(f"[SUCCESS] Exported {NUM_RECORDS} rows to customers.csv")

    # ==========================================
    # 2. Products Dataset Generation
    # ==========================================
    print("[INFO] Processing products dataset...")
    products = []
    categories = ['Electronics', 'Clothing', 'Home', 'Books']
    
    for i in range(1, NUM_RECORDS + 1):
        product_name = fake.word().title() + " " + fake.word().title()
        # Anomaly Injection: 5% inconsistent text formatting (whitespaces/casing)
        if random.random() < 0.05: 
            product_name = f"  {product_name.lower()}  " if random.choice([True, False]) else product_name.upper()
            
        products.append({
            'product_id': f"PROD_{i:04d}", 
            'product_name': product_name, 
            'category': random.choice(categories), 
            'subcategory': fake.word(), 
            'cost_price': round(random.uniform(10.0, 5000.0), 2)
        })
        
    df_products = pd.DataFrame(products)
    df_products.to_csv(f'{OUTPUT_DIR}/products.csv', index=False)
    print(f"[SUCCESS] Exported {NUM_RECORDS} rows to products.csv")

    # ==========================================
    # 3. Orders Dataset Generation
    # ==========================================
    print("[INFO] Processing orders dataset...")
    orders = []
    statuses = ['PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED']
    customer_ids = df_customers['customer_id'].tolist()
    
    for i in range(1, NUM_RECORDS + 1):
        # Anomaly Injection: 5% missing relational references (NULL customer_id)
        c_id = np.nan if random.random() < 0.05 else random.choice(customer_ids) 
        
        order_date_obj = fake.date_time_between(start_date='-1y', end_date='now')
        order_date = order_date_obj.strftime('%Y-%m-%d %H:%M:%S')
        
        # Anomaly Injection: 5% inconsistent date parsing formats (DD-MM-YYYY)
        if random.random() < 0.05: 
            order_date = order_date_obj.strftime('%d-%m-%Y %H:%M:%S') 
            
        orders.append({
            'order_id': f"ORD_{i:05d}", 
            'customer_id': c_id, 
            'order_date': order_date, 
            'status': random.choice(statuses), 
            'region_code': random.choice(REGION_CODES)
        })
        
    df_orders = pd.DataFrame(orders)
    df_orders.to_csv(f'{OUTPUT_DIR}/orders.csv', index=False)
    print(f"[SUCCESS] Exported {NUM_RECORDS} rows to orders.csv")

    # ==========================================
    # 4. Order Items Dataset Generation
    # ==========================================
    print("[INFO] Processing order items dataset...")
    order_items = []
    order_ids = df_orders['order_id'].dropna().tolist()
    product_ids = df_products['product_id'].tolist()
    
    # Generating N+500 records to ensure transactional volume & multi-item orders
    for i in range(1, NUM_RECORDS + 500):
        qty = random.randint(1, 10)
        # Anomaly Injection: 3% negative quantities representing returns/refund structural issues
        if random.random() < 0.03: 
            qty = -qty 
            
        order_items.append({
            'item_id': f"ITEM_{i:05d}", 
            'order_id': random.choice(order_ids), # Ensures core referential validation
            'product_id': random.choice(product_ids), 
            'quantity': qty, 
            'unit_price': round(random.uniform(20.0, 6000.0), 2), 
            'discount_percent': round(random.uniform(0.0, 100.0), 2)
        })
        
    df_order_items = pd.DataFrame(order_items)
    df_order_items.to_csv(f'{OUTPUT_DIR}/order_items.csv', index=False)
    print(f"[SUCCESS] Exported {len(df_order_items)} rows to order_items.csv")

    print(f"\n[INFO] Pipeline executed successfully. Raw datasets systematically exported to: {os.path.abspath(OUTPUT_DIR)}")

if __name__ == "__main__":
    generate_raw_data()