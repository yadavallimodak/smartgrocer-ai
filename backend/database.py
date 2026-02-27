import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "grocery_inventory.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create inventory table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        aisle INTEGER,
        stock INTEGER,
        price REAL
    )
    ''')
    
    # Insert mock data if empty
    cursor.execute("SELECT COUNT(*) FROM inventory")
    if cursor.fetchone()[0] == 0:
        mock_data = [
            ("Organic Milk", "Dairy", 1, 15, 4.99),
            ("Eggs (1 Dozen)", "Dairy", 1, 30, 3.50),
            ("Whole Wheat Bread", "Bakery", 2, 20, 3.99),
            ("Gluten-Free Bread", "Bakery", 2, 5, 5.99),
            ("Apples", "Produce", 3, 50, 1.20),
            ("Bananas", "Produce", 3, 40, 0.50),
            ("Tomatoes", "Produce", 3, 60, 0.89),
            ("Garlic", "Produce", 3, 40, 0.50),
            ("Yellow Onion", "Produce", 3, 45, 0.75),
            ("Olive Oil", "Pantry", 7, 20, 8.99),
            ("Fresh Basil", "Produce", 3, 15, 2.99),
            ("Dried Oregano", "Pantry", 7, 30, 3.49),
            ("Salt", "Pantry", 7, 50, 1.50),
            ("Black Pepper", "Pantry", 7, 50, 2.50),
            ("Spaghetti", "Pantry", 8, 40, 1.99),
            ("Crushed Tomatoes", "Pantry", 8, 0, 2.49), # Intentionally out of stock for fallback testing
            ("Chicken Breast", "Meat", 4, 10, 8.50),
            ("Vegan Burgers", "Frozen", 5, 2, 6.99),
            ("Orange Juice", "Beverages", 6, 25, 4.50),
            ("Oat Milk", "Dairy", 1, 0, 4.99), # Out of stock item
        ]
        cursor.executemany("INSERT INTO inventory (name, category, aisle, stock, price) VALUES (?, ?, ?, ?, ?)", mock_data)
        
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
