from fastmcp import FastMCP
from dotenv import load_dotenv
import sqlite3
import os

load_dotenv()  

DB_NAME = os.getenv("DB_NAME", "expenses.db")

DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)
CATEGORY_PATH = os.path.join(os.path.dirname(__file__), "category.json")

mcp = FastMCP(name="Expense Tracking MCP")

def init_db():
    """Initializes the SQLite database and creates the expenses table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                date DATE NOT NULL DEFAULT (CURRENT_DATE),
                category TEXT DEFAULT (Miscellaneous),
                subcategory TEXT DEFAULT (Other)
            )
        ''')
        conn.commit()

init_db()

@mcp.tool
def add_expense(description: str, amount: float, category: str | None = None, subcategory: str | None = None, date: str | None = None) -> str:
    """
    Adds a new expense to the database.
    Args
        description (str): The description of the expense.
        amount (float): The amount of the expense.
        category (str | None): The category of the expense. If None, it defaults to "Miscellaneous".
        subcategory (str | None): The subcategory of the expense. If None, it defaults to "Other".
        date (str | None): The date of the expense. If None, the current date is used.
    Returns
        str: A message indicating the expense was added successfully.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if date is None:
            cursor.execute('''
                INSERT INTO expenses (description, amount, category, subcategory)
                VALUES (?, ?, ?, ?)
            ''', (description, amount, category, subcategory))
        else:
            cursor.execute('''
                INSERT INTO expenses (description, amount, date)
                VALUES (?, ?, ?)
            ''', (description, amount, date))
        conn.commit()
    return "Expense added successfully."

@mcp.tool
def get_all_expenses() -> list[dict]:
    """
    Retrieves all expenses from the database.
    Returns
        list[dict]: A list of all expenses.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM expenses')
        rows = cursor.fetchall()
        expenses = [{"id": row[0], "description": row[1], "amount": row[2], "date": row[3], "category": row[4], "subcategory": row[5]} for row in rows]
    return expenses

@mcp.tool
def get_expense_between_dates(start_date: str, end_date: str) -> list[dict]:
    """
    Retrieves expenses between two dates.
    Args
        start_date (str): The start date.
        end_date (str): The end date.
    Returns
        list[dict]: A list of expenses between the two dates.
    """
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM expenses
            WHERE date BETWEEN ? AND ?
        ''', (start_date, end_date))
        rows = cursor.fetchall()
        expenses = [{"id": row[0], "description": row[1], "amount": row[2], "date": row[3], "category": row[4], "subcategory": row[5]} for row in rows]
    return expenses

@mcp.resource("expense://categories", mime_type="application/json" , description="Provides a list of expense categories and subcategories.")
def categories()-> dict:
    """
    Provides a list of expense categories and subcategories.
    Returns
        dict: A dictionary containing categories and their corresponding subcategories.
    """
    import json
    with open(CATEGORY_PATH, 'r') as f:
        categories = json.load(f)
    return categories

if __name__ == "__main__":
    mcp.run()