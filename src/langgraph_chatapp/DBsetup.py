
import sqlite3

def setup_database():
    with sqlite3.connect("customer_support.db") as conn:
        cur = conn.cursor()

        # Create tables
        cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            status TEXT,
            delivery_date TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            issue TEXT,
            status TEXT DEFAULT 'open',
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
        """)

        # Insert some demo customers
        cur.execute("INSERT OR IGNORE INTO customers (name, email) VALUES (?, ?)", 
                    ("Alice Khan", "alice@example.com"))
        cur.execute("INSERT OR IGNORE INTO customers (name, email) VALUES (?, ?)", 
                    ("Bilal Ahmed", "bilal@example.com"))

        # Insert some demo orders
        cur.execute("INSERT OR IGNORE INTO orders (order_id, customer_id, status, delivery_date) VALUES (?, ?, ?, ?)", 
                    (1001, 1, "Shipped", "2025-09-10"))
        cur.execute("INSERT OR IGNORE INTO orders (order_id, customer_id, status, delivery_date) VALUES (?, ?, ?, ?)", 
                    (1002, 2, "Processing", "2025-09-12"))

        # Insert a demo ticket
        cur.execute("INSERT OR IGNORE INTO tickets (ticket_id, customer_id, issue, status) VALUES (?, ?, ?, ?)", 
                    (1, 1, "Package damaged", "open"))

        conn.commit()
    return "Database Function Successful"


status=setup_database()
print(status)

