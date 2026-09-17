### Command to Run the MCP inspector
```bash
uv run fastmcp dev inspector main.py
```
- Inspector is like a POSTMAN to MCP server (or like SWAGGER UI)
![mcp inspector](./images/inspector_ui.png)
- Tools
![demo-server-tools](./images/tools.png)

### Expense Tracker MCP
- Tool Call
![tool-call](./images/expense_tracker_tool.png)
- Resource/Get
![resouce-get](./images/expense_tracker_resource.png)

### Remote MCP
- Deploy with `fastmcp.cloud` by connecting your GitHub repo
- Expense-tracking-mcp deployed on [URL](https://expense-tracking-mcp.fastmcp.app/mcp)
    1. However the mcp is better to use locally, because
    2. No user authentication
    3. No user level separation of expenses