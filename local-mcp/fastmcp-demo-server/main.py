from fastmcp import FastMCP
import random

mcp = FastMCP(name="FastMCP Demo Server")

@mcp.tool
def roll_dice(n: int = 1, sides: int = 6) -> list[int]:
    """Rolls n dice with the specified number of sides."""
    if n < 1 or sides < 1:
        raise ValueError("Number of dice and sides must be positive integers.")
    
    rolls = [random.randint(1, sides) for _ in range(n)]
    return rolls

@mcp.tool
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers together."""
    return a + b

if __name__ == "__main__":
    mcp.run()