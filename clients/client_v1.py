import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

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
    tool_list = await client.get_tools()
    tools = {tool.name: tool for tool in tool_list}

    prompt = HumanMessage(content="What is the total expense in this month of September 2026?")

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    llm_tools =llm.bind_tools(tool_list)

    response = await llm_tools.ainvoke([prompt])

    if not getattr(response, "tool_calls", None):
        print("No tool calls were made by the LLM.")
        print("LLM response:")
        print(response.text)
        return

    for i, tool_obj in enumerate(response.tool_calls):
        print("-"*40)
        print(f"Tool call {i + 1}:")
        print(f"Calling tool: {tool_obj['name']}")
        print(f"Tool input: {tool_obj['args']}")
        print("-"*40)

    print("Tool result:")
    tool_result = await tools[response.tool_calls[0]['name']].ainvoke(response.tool_calls[0]['args'])
    print(tool_result)
    tool_message = ToolMessage(content=tool_result, tool_call_id=response.tool_calls[0]['id'], name=response.tool_calls[0]['name'])
    final_response = await llm_tools.ainvoke([prompt, response, tool_message])
    print("\nFinal response from LLM:")
    print(final_response.text)

if __name__ == "__main__":
    asyncio.run(main())