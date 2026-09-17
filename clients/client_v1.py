import asyncio
import json
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

FMCP_ACCESS_KEY = os.getenv("FMCP_ACCESS_KEY")
REMOTE_MCP_SERVER_URL = os.getenv("REMOTE_MCP_SERVER_URL")

servers = {
    "local_expense_server": {
        "transport": "stdio",
        "command": r"D:\hr\my-mcp-servers\.venv\Scripts\fastmcp.exe",
        "args": [
            "run",
            r"D:\hr\my-mcp-servers\local-mcp\expense-tracking-mcp\main.py"
        ],
    },
    "remote_expense_server": {
        "transport": "http",
        "url": REMOTE_MCP_SERVER_URL,
        "headers": {
            "Authorization": f"Bearer {FMCP_ACCESS_KEY}"
        }
    }
}

async def main():
    print("Starting MultiServerMCPClient...")
    client = MultiServerMCPClient(servers)
    tool_list = await client.get_tools()
    tools = {tool.name: tool for tool in tool_list}
    print(f"Available tools: {list(tools.keys())}")

    prompt = HumanMessage(content="What is the total expense in this month of September 2026?")

    llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    llm_tools =llm.bind_tools(tool_list)

    final_response = await invoke_with_tools(prompt, llm_tools, tools)
    print("LLM response:")
    print(final_response.text)


async def invoke_with_tools(prompt, llm_with_tools, tools):
    """Invoke the LLM and handle tool calls until a final response is returned."""
    messages = [prompt]
    tool_call_number = 0

    while True:
        response = await llm_with_tools.ainvoke(messages)
        messages.append(response)

        if not getattr(response, "tool_calls", None):
            return response

        for tool_obj in response.tool_calls:
            tool_call_number += 1
            tool_name = tool_obj["name"]
            tool_args = tool_obj["args"]
            tool_id = tool_obj["id"]
            print(f"Tool call {tool_call_number}: {tool_name}")
            result = await tools[tool_name].ainvoke(tool_args)
            messages.append(ToolMessage(content=json.dumps(result), tool_call_id=tool_id))

if __name__ == "__main__":
    asyncio.run(main())