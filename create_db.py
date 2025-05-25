import sqlite3
import os

os.makedirs("db", exist_ok=True)

conn = sqlite3.connect("db/sample.db")
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS employees")
cursor.execute("DROP TABLE IF EXISTS customers")

# Create customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    city TEXT,
    country TEXT
)
""")

# Create orders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    product TEXT,
    amount DECIMAL(10,2),
    order_date DATE,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

# Create employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    department TEXT,
    salary DECIMAL(10,2),
    hire_date DATE
)
""")

# Insert sample customers
cursor.executemany("""
INSERT INTO customers (name, email, city, country) VALUES (?, ?, ?, ?)
""", [
    ("Alice Smith", "alice@email.com", "Boston", "USA"),
    ("Bob Johnson", "bob@email.com", "New York", "USA"),
    ("Charlie Brown", "charlie@email.com", "Boston", "USA"),
    ("David Wilson", "david@email.com", "Chicago", "USA"),
    ("Emma Davis", "emma@email.com", "London", "UK")
])

# Insert sample orders
cursor.executemany("""
INSERT INTO orders (customer_id, product, amount, order_date) VALUES (?, ?, ?, ?)
""", [
    (1, "Laptop", 1200.00, "2025-01-15"),
    (1, "Mouse", 25.00, "2025-01-15"),
    (2, "Monitor", 300.00, "2025-01-16"),
    (3, "Keyboard", 80.00, "2025-01-17"),
    (4, "Printer", 200.00, "2025-01-18")
])

# Insert sample employees
cursor.executemany("""
INSERT INTO employees (name, department, salary, hire_date) VALUES (?, ?, ?, ?)
""", [
    ("John Smith", "Sales", 50000.00, "2024-01-01"),
    ("Sarah Jones", "Sales", 52000.00, "2024-02-15"),
    ("Mike Brown", "IT", 60000.00, "2024-03-01"),
    ("Lisa Wilson", "HR", 55000.00, "2024-01-10"),
    ("Tom Davis", "IT", 65000.00, "2023-12-01")
])

conn.commit()
conn.close()

print("Database and tables created with sample data.")
