import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

servers =  {
    "local_expense_server" : {
        "transport" : "stdio",
        "command" : "D:\\hr\\my-mcp-servers\\.venv\\Scripts\\fastmcp.exe",
        "args": [
            "run",
            "D:\\hr\\my-mcp-servers\\local-mcp\\expense-tracking-mcp\\main.py"
        ]
    }
}

async def main():
    print("Starting MultiServerMCPClient...")
    client = MultiServerMCPClient(servers=servers)

if __name__ == "__main__":
    asyncio.run(main())