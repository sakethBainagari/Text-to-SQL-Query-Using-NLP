import streamlit as st
from model import text_to_sql, SCHEMA_INFO

st.set_page_config(page_title="Text to SQL Converter", layout="wide")

# Title and description
st.title("💬 Text to SQL Query Generator")
st.write("Enter your question in natural language, and get the corresponding SQL query.")

# Sidebar with schema and examples
with st.sidebar:
    st.header("📚 Database Schema")
    st.code(SCHEMA_INFO, language="sql")
    
    st.header("📝 Example Questions")
    st.markdown("""
    Try these examples:
    - Show all customers from Boston
    - List employees in Sales department
    - Show products ordered by Alice
    - Find total orders amount by customer
    - List employees with salary above 55000
    - Count orders by city
    """)

# Main query input
query = st.text_area(
    "Enter your question:",
    height=100,
    placeholder="e.g., Show all customers from Boston",
    help="Type your question in natural language and press Ctrl+Enter or click the button below"
)

# Convert button
if st.button("Generate SQL Query", type="primary") or query:
    if query:
        try:
            # Generate SQL
            sql = text_to_sql(query)
            
            # Show the generated SQL in a bigger box
            st.subheader("Generated SQL Query:")
            st.code(sql, language='sql')
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Try rephrasing your question or check the example queries in the sidebar.")
    else:
        st.info("Please enter a question above.") 