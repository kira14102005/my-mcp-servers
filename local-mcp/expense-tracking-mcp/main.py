from fastmcp import FastMCP
from dotenv import load_dotenv
import aiosqlite
import asyncio
import aiofiles
import os
import json

load_dotenv()  

DB_NAME = os.getenv("DB_NAME", "expenses.db")
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)
CATEGORY_PATH = os.path.join(os.path.dirname(__file__), "category.json")

mcp = FastMCP(name="Expense Tracking MCP")

async def init_db():
    """Initializes the SQLite database and creates the expenses table if it doesn't exist."""
    async with aiosqlite.connect(DB_PATH) as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                date DATE NOT NULL DEFAULT (CURRENT_DATE),
                category TEXT DEFAULT 'Miscellaneous',
                subcategory TEXT DEFAULT 'Other'
            )
        ''')
        await conn.commit()

@mcp.tool
async def add_expense(
    description: str, 
    amount: float, 
    category: str | None = None, 
    subcategory: str | None = None, 
    date: str | None = None
) -> str:
    """Adds a new expense to the database."""
    async with aiosqlite.connect(DB_PATH) as conn:
        columns = ["description", "amount"]
        values = [description, amount]

        if category:
            columns.append("category")
            values.append(category)
        if subcategory:
            columns.append("subcategory")
            values.append(subcategory)
        if date:
            columns.append("date")
            values.append(date)

        placeholders = ", ".join("?" for _ in values)
        await conn.execute(
            f"INSERT INTO expenses ({', '.join(columns)}) VALUES ({placeholders})",
            values,
        )
        await conn.commit()

    return "Expense added successfully."

@mcp.tool
async def get_all_expenses() -> list[dict]:
    """Retrieves all expenses from the database."""
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('SELECT * FROM expenses') as cursor:
            rows = await cursor.fetchall()

    return [{"id": row[0], "description": row[1], "amount": row[2], "date": row[3], "category": row[4], "subcategory": row[5]} for row in rows]

@mcp.tool
async def get_expense_between_dates(start_date: str, end_date: str) -> list[dict]:
    """Retrieves expenses between two dates."""
    async with aiosqlite.connect(DB_PATH) as conn:
        async with conn.execute('''
            SELECT * FROM expenses
            WHERE date BETWEEN ? AND ?
        ''', (start_date, end_date)) as cursor:
            rows = await cursor.fetchall()
   
    return [{"id": row[0], "description": row[1], "amount": row[2], "date": row[3], "category": row[4], "subcategory": row[5]} for row in rows]

@mcp.tool
async def summarize(start_date: str, end_date: str, category: str | None = None) -> dict:
    """Summarizes expenses between two dates."""
    async with aiosqlite.connect(DB_PATH) as conn:
        sql_query = "SELECT SUM(amount), COUNT(*) FROM expenses WHERE date BETWEEN ? AND ?"
        values = (start_date, end_date)
        if category:
            sql_query += " AND category = ?"
            values += (category,)

        async with conn.execute(sql_query, values) as cursor:
            total_amount, count = await cursor.fetchone()
        
    return {"total_amount": total_amount or 0, "count": count or 0, "category": category or "All"}

@mcp.resource("expense://categories", mime_type="application/json", description="Provides a list of expense categories and subcategories.")
async def categories() -> dict:
    """Provides a list of expense categories and subcategories."""
    async with aiofiles.open(CATEGORY_PATH, 'r') as f:
        data_str = await f.read()

    return json.loads(data_str)

if __name__ == "__main__":
    asyncio.run(init_db())
    mcp.run()