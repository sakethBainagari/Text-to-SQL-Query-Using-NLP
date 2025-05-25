import sqlite3
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import re

# Load the T5 model and tokenizer
model_name = "mrm8488/t5-base-finetuned-wikiSQL"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Database schema information
SCHEMA_INFO = """
Tables and their columns:
1. customers: id, name, email, city, country
2. orders: id, customer_id (references customers.id), product, amount, order_date
3. employees: id, name, department, salary, hire_date
"""

# Template queries for common questions
QUERY_TEMPLATES = {
    # Customer queries
    r"show (?:all )?customers from (.+)": 
        lambda city: f"SELECT * FROM customers WHERE LOWER(city) = LOWER('{city.strip()}');",
    
    r"show (?:all )?customers": 
        "SELECT * FROM customers;",
    
    # Employee queries
    r"(?:show|list) (?:all )?employees from (.+)":
        lambda city: f"SELECT * FROM employees WHERE LOWER(city) = LOWER('{city.strip()}');",
        
    r"(?:show|list) (?:all )?employees in (.+)": 
        lambda dept: f"SELECT * FROM employees WHERE LOWER(department) = LOWER('{dept.strip()}');",
    
    r"(?:show|list) employees with salary above (.+)": 
        lambda amount: f"SELECT * FROM employees WHERE salary > {float(amount.strip())};",
        
    r"show (?:all )?employees": 
        "SELECT * FROM employees;",
    
    # Order queries
    r"show (?:all )?orders from (.+)":
        lambda city: f"""SELECT o.* FROM orders o 
        JOIN customers c ON o.customer_id = c.id 
        WHERE LOWER(c.city) = LOWER('{city.strip()}');""",
    
    r"show (?:all )?orders": 
        "SELECT * FROM orders;",
    
    r"show products ordered by (.+)": 
        lambda name: f"""SELECT o.product, o.amount, o.order_date 
        FROM orders o 
        JOIN customers c ON o.customer_id = c.id 
        WHERE LOWER(c.name) LIKE LOWER('%{name.strip()}%');""",
    
    r"(?:show|get|find) total orders amount by customer": 
        """SELECT c.name, SUM(o.amount) as total_amount 
        FROM customers c 
        LEFT JOIN orders o ON c.customer_id = o.id 
        GROUP BY c.name;""",
    
    r"count orders by city":
        """SELECT c.city, COUNT(o.id) as order_count
        FROM customers c
        LEFT JOIN orders o ON c.customer_id = o.id
        GROUP BY c.city;"""
}

def clean_sql(sql):
    """Clean and format the SQL query."""
    sql = sql.strip()
    
    # Ensure it ends with semicolon
    if not sql.endswith(';'):
        sql += ';'
    
    # Remove any newlines and extra spaces
    sql = re.sub(r'\s+', ' ', sql)
    
    return sql.strip()

def text_to_sql(question):
    """Convert natural language question to SQL query."""
    try:
        # 1. First try to match with templates
        question = question.strip().lower()
        
        # Basic validation of entity-attribute combinations
        if "customers" in question and "department" in question:
            raise ValueError("Customers do not have departments. Only employees have departments.")
        if "orders" in question and "department" in question:
            raise ValueError("Orders do not have departments. Only employees have departments.")
        if "employees" in question and "city" in question:
            raise ValueError("Employees do not have cities. Only customers have cities.")
            
        for pattern, template in QUERY_TEMPLATES.items():
            match = re.match(pattern, question, re.IGNORECASE)
            if match:
                if callable(template):
                    # If template is a function, call it with the captured groups
                    return clean_sql(template(*match.groups()))
                else:
                    # If template is a string, use it directly
                    return clean_sql(template)
        
        # 2. If no template matches, use the T5 model
        prompt = f"Convert to SQL: {question}\nSchema: {SCHEMA_INFO}\nSQL:"
        
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(
            **inputs,
            max_length=128,
            num_beams=5,
            early_stopping=True,
            no_repeat_ngram_size=2
        )
        sql = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Basic validation of model output
        sql = clean_sql(sql)
        if not sql.upper().startswith('SELECT'):
            raise ValueError(f"Generated SQL does not start with SELECT: {sql}")
        
        return sql
        
    except Exception as e:
        print(f"Error in text_to_sql: {str(e)}")
        raise ValueError(f"Failed to generate SQL query: {str(e)}")

def get_connection():
    """Get a connection to the SQLite database."""
    return sqlite3.connect("db/sample.db")

def run_query(sql):
    """Execute SQL query and return results."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Print the SQL being executed (for debugging)
        print(f"Executing SQL: {sql}")
        
        cursor.execute(sql)
        results = cursor.fetchall()
        return results
        
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        raise Exception(f"Database error: {str(e)}")
    finally:
        if conn:
            conn.close()

# Attach the get_connection function to run_query for column name retrieval
run_query.get_connection = get_connection
