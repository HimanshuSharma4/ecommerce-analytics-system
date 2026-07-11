# E-Commerce Order Analytics System 📊

An end-to-end Data Engineering and Analytics pipeline built with Python and SQLite. This project demonstrates the ability to generate, clean, process, and analyze complex e-commerce datasets while handling intentional anomalies and edge cases.

## 🚀 Project Architecture

The system is divided into 5 distinct phases:
1. **Data Generation:** Synthetic data creation (`faker`, `pandas`) simulating raw e-commerce data with intentional anomalies (NULLs, invalid formats, negative quantities).
2. **Data Cleaning:** Automated ETL processes to normalize text, fix date formats, validate emails using Regex, and enforce referential integrity.
3. **Database Integration:** Local SQLite database setup mapping cleaned datasets to relational tables.
4. **SQL Analysis:** 16 Advanced queries (using CTEs, Window Functions, LAG/LEAD, NTILE) for business intelligence reporting.
5. **CLI Reporting Tool:** A native Python command-line interface for generating real-time executive summaries based on custom date ranges.

## 📁 Repository Structure

```text
ecommerce-analytics-system/
│
├── data/                  # Local datasets (Ignored in version control)
│   ├── raw/               # Messy CSV files generated in Phase 1
│   ├── cleaned/           # Validated CSV files from Phase 2
│   └── ecommerce.db       # SQLite relational database
│
├── scripts/               # Python ETL and Testing Modules
│   ├── generate_data.py   # Synthesizes 500+ rows of anomalous data
│   ├── clean_data.py      # Cleans datasets and generates Validation Report
│   ├── load_database.py   # Automates SQLite table creation and data loading
│   ├── report_cli.py      # Interactive Command-Line Reporting Tool
│   └── test_edge_cases.py # Unit tests for anomaly handling (100% Pass)
│
├── sql/                   # Analytical Queries
│   └── queries.sql        # Contains 16 queries (Aggregations, CTEs, Window Functions)
│
├── .gitignore             # Security and environment exclusions
└── README.md              # Project documentation
```

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Libraries:** `pandas`, `numpy`, `faker`, `sqlite3`, `re`, `datetime`
* **Database:** SQLite3
* **Concepts:** ETL Pipelines, Data Normalization, Referential Integrity, Advanced SQL Analytics.

## ⚙️ How to Run Locally

1. **Setup Environment:**
   ```bash
   pip install pandas numpy faker
   ```
2. **Generate Raw Data:**
   ```bash
   cd scripts
   python generate_data.py
   ```
3. **Clean and Validate Data:**
   ```bash
   python clean_data.py
   ```
4. **Load into SQLite Database:**
   ```bash
   python load_database.py
   ```
5. **Run the Interactive CLI Report:**
   ```bash
   python report_cli.py
   ```
6. **Execute Edge Case Unit Tests:**
   ```bash
   python test_edge_cases.py
   ```

## 🛡️ Edge Case Handling
The system includes robust unit testing to handle:
* Orphaned `order_items` referencing non-existent `order_id`s.
* Logical bound validations (e.g., `discount_percent` > 100 or < 0).
* Zero-quantity transactions.
* Future `order_date` timestamp restrictions.