import asyncio
import json
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

    tool_messages = []
    for i, tool_obj in enumerate(response.tool_calls):
        tool_name = tool_obj['name']
        tool_args = tool_obj['args']
        tool_id = tool_obj['id']
        print(f"Tool call {i+1}: {tool_name}")
        result = await tools[tool_name].ainvoke(tool_args)
        tool_messages.append(ToolMessage(content=json.dumps(result), tool_call_id=tool_id, name=tool_name))

    final_response = await llm_tools.ainvoke([prompt, response, *tool_messages])
    print("LLM response:")
    print(final_response.text)

if __name__ == "__main__":
    asyncio.run(main())