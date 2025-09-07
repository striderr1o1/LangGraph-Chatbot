
from groq import Groq
import os
from dotenv import load_dotenv
import re
import ast
load_dotenv()
import sqlite3
schema = """customers(customer_id, name, email)
orders(order_id, customer_id, status, delivery_date)
tickets(ticket_id, customer_id, issue, status)

Relationships:
- orders.customer_id → customers.customer_id
- tickets.customer_id → customers.customer_id"""

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)
def generateQuery(state):
    query = state["query"]
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are an SQL query generator based on analyzing the user query. Dont give even a single word other than the query. Here is the schema: {schema}. Return a single valid SQL query string for sqlite3, no comments, no explanations """
            },
            {
                "role":"user", "content":f"""Here is the user question: {query}...make an SQL query based on user requirements. Return only SQL inside ```sql ... ``` block."""
            }
        ]
    )
    llm1Query = response.choices[0].message.content
    
    finalResponse = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are an SQL query analyzer that uses sqllite3. You get the SQL query and you look verify if its right. If its wrong, you correct it without delivering any other talk other than the query. Here is the schema: {schema}. Make query according to sqLite database."""
            },
            {
                "role":"user", "content":f"""Here is the user question: {query}...fix this if theres any mistake in this previously generated SQL query: {llm1Query}. Return only SQL inside ```sql ... ``` block. If its multiple queries, return a single valid SQL query string, no comments, no explanations"""
            }
        ]
    )
    llm2query = finalResponse.choices[0].message.content
    state["results"] = llm2query
    #add parser maybe

def parse_sql(state):
    """
    Extracts SQL query from LLM response.

    Args:
        llm_response (str): Text returned by the LLM, may contain explanations or code blocks.

    Returns:
        str: The extracted SQL query, or empty string if none found.
    """
    # Try to extract from ```sql ... ``` block
    match = re.search(r"```sql\s*(.*?)\s*```", state["results"], re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # Fallback: try ``` ... ``` block without specifying language
    match = re.search(r"```\s*(.*?)\s*```", state["results"], re.DOTALL)
    if match:
        return match.group(1).strip()

    # Fallback: assume last line ending with semicolon is the SQL
    lines = state["results"].strip().splitlines()
    for line in reversed(lines):
        if ";" in line:
            return line.strip()

    # If all else fails, return empty string
    return ""




def run_query(state, sql_query):
    """
    Executes a SQL query on the given SQLite database.

    Args:
        db_path (str): Path to SQLite database file.
        sql_query (str): The SQL query to execute.

    Returns:
        list[tuple]: Query results as list of rows (tuples).
    """
    try:
        with sqlite3.connect("customer_support.db") as conn:
            cur = conn.cursor()
            cur.execute(sql_query)
            # If it's a SELECT, fetch results
            if str(sql_query).strip().lower().startswith("select"):
                results = cur.fetchall()
                state["sql_results"] = results
            else:
            # If it's INSERT/UPDATE/DELETE, commit changes
               conn.commit()
               state["sql_results"] = [("Query executed successfully",None)]
    
    except sqlite3.Error as e:
        state["sql_results"] = [(f"Error executing query: {e}",None)]
  
