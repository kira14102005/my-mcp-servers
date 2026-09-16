from fastmcp import FastMCP
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()  

DB_NAME = os.getenv("DB_NAME", "expenses.db")

DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

mcp = FastMCP(name="Expense Tracking MCP")

def init_db():
    """Initializes the SQLite database and creates the expenses table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

@mcp.tool
def add_expense(description: str, amount: float, date: str) -> str:
    """Adds a new expense to the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (description, amount, date)
            VALUES (?, ?, ?)
        ''', (description, amount, date))
        conn.commit()
    return "Expense added successfully."

@mcp.tool
def get_expenses() -> list[dict]:
    """Retrieves all expenses from the database."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses')
        rows = cursor.fetchall()
        expenses = [{"id": row[0], "description": row[1], "amount": row[2], "date": row[3]} for row in rows]
    return expenses

if __name__ == "__main__":
    mcp.run()