import sqlite3
import os
from datetime import datetime, timedelta

# Configuration Constants
DB_PATH = '../data/ecommerce.db'

def get_db_connection():
    """Establishes connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database not found at {DB_PATH}. Please run load_database.py first.")
        exit(1)
    return sqlite3.connect(DB_PATH)

def calculate_previous_period(start_date, end_date):
    """Calculates the exact previous date range for Year-over-Year or Period-over-Period comparison."""
    delta = end_date - start_date
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - delta
    return prev_start_date, prev_end_date

def fetch_metrics(start_str, end_str):
    """Fetches Total Orders, Revenue, and Unique Customers for a given date range."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS unique_customers,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2) AS total_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.order_date >= ? AND o.order_date <= ?
    """
    # Appending time to ensure full day coverage
    cursor.execute(query, (start_str + " 00:00:00", end_str + " 23:59:59"))
    result = cursor.fetchone()
    conn.close()
    
    return {
        'orders': result[0] or 0,
        'customers': result[1] or 0,
        'revenue': result[2] or 0.0
    }

def fetch_top_products(start_str, end_str):
    """Fetches the Top 3 products by revenue for the given period."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT 
            p.product_name,
            ROUND(SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)), 2) AS product_revenue
        FROM orders o
        JOIN order_items oi ON o.order_id = oi.order_id
        JOIN products p ON oi.product_id = p.product_id
        WHERE o.order_date >= ? AND o.order_date <= ?
        GROUP BY p.product_id
        ORDER BY product_revenue DESC
        LIMIT 3
    """
    cursor.execute(query, (start_str + " 00:00:00", end_str + " 23:59:59"))
    results = cursor.fetchall()
    conn.close()
    return results

def calculate_percentage_change(current, previous):
    """Safely calculates percentage change between two values."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 2)

def generate_report():
    """Main CLI logic for user interaction and report generation."""
    print("="*60)
    print(" 🚀 E-COMMERCE ORDER ANALYTICS SYSTEM - REPORTING CLI")
    print("="*60)
    
    # 1. User Inputs
    print("\nSelect Report Type:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    print("4. Custom Date Range")
    
    choice = input("Enter choice (1-4): ").strip()
    
    start_str = ""
    end_str = ""
    
    if choice in ['1', '2', '3', '4']:
        print("\n[INFO] For testing, enter dates between 2024-01-01 and today.")
        start_str = input("Enter Start Date (YYYY-MM-DD): ").strip()
        end_str = input("Enter End Date (YYYY-MM-DD): ").strip()
    else:
        print("[ERROR] Invalid choice. Exiting.")
        return

    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_str, '%Y-%m-%d')
    except ValueError:
        print("[ERROR] Invalid date format. Please use YYYY-MM-DD.")
        return

    # 2. Process Dates & Fetch Data
    prev_start_date, prev_end_date = calculate_previous_period(start_date, end_date)
    
    prev_start_str = prev_start_date.strftime('%Y-%m-%d')
    prev_end_str = prev_end_date.strftime('%Y-%m-%d')

    print(f"\n[INFO] Generating report for: {start_str} to {end_str}")
    print(f"[INFO] Comparing with previous period: {prev_start_str} to {prev_end_str}\n")

    current_metrics = fetch_metrics(start_str, end_str)
    previous_metrics = fetch_metrics(prev_start_str, prev_end_str)
    top_products = fetch_top_products(start_str, end_str)

    # 3. Calculate Comparisons
    revenue_change = calculate_percentage_change(current_metrics['revenue'], previous_metrics['revenue'])
    orders_change = calculate_percentage_change(current_metrics['orders'], previous_metrics['orders'])

    # 4. Display Report
    print("="*60)
    print(" 📊 EXECUTIVE SUMMARY REPORT")
    print("="*60)
    print(f"Total Revenue      : ${current_metrics['revenue']:,.2f} ({revenue_change:+.2f}% vs prev period)")
    print(f"Total Orders       : {current_metrics['orders']} ({orders_change:+.2f}% vs prev period)")
    print(f"Unique Customers   : {current_metrics['customers']}")
    
    print("\n🏆 TOP 3 PRODUCTS (By Revenue)")
    print("-" * 30)
    if not top_products:
        print("No products sold in this period.")
    else:
        for i, product in enumerate(top_products, 1):
            print(f"{i}. {product[0][:25]:<25} | ${product[1]:,.2f}")
    print("="*60 + "\n")

if __name__ == "__main__":
    generate_report()