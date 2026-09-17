import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

servers = {
    "local_expense_server": {
        "transport": "stdio",
        "command": r"D:\hr\my-mcp-servers\.venv\Scripts\fastmcp.exe",
        "args": [
            "run",
            r"D:\hr\my-mcp-servers\local-mcp\expense-tracking-mcp\main.py"
        ],
    }
}

async def main():
    print("Starting MultiServerMCPClient...")
    client = MultiServerMCPClient(servers)
    tools = await client.get_tools()
    print("Tools retrieved from servers:")
    print(tools)

if __name__ == "__main__":
    asyncio.run(main())