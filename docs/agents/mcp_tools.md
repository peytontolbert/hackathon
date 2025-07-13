# MCP Tools Reference

## Core MCP Tools

These are the three essential tools for MCP integration:

### 1. search_tools(query)
```python
@staticmethod
@tool("Search MCP tools")
def search_tools(query: str) -> str:
    """Search for tools using natural language query"""
```
- **Purpose**: Search for tools using natural language
- **Method**: tools/call
- **Arguments**: 
  - query: Natural language search
  - max_results: 5
- **Returns**: Raw response text with search results

### 2. get_tool_detail(tool_id)
```python
@staticmethod
@tool("Get tool details")
def get_tool_detail(tool_id: str) -> str:
    """Get detailed information about a specific tool"""
```
- **Purpose**: Get detailed info about a specific tool
- **Method**: tools/call
- **Arguments**: 
  - tool_id: ID of the tool to look up
- **Returns**: Raw response text with tool details

### 3. add_mcp_tool(tool_id)
```python
@staticmethod
@tool("Add MCP tool")
def add_mcp_tool(tool_id: str) -> str:
    """Add an MCP tool to configuration"""
```
- **Purpose**: Add a tool to MCP configuration
- **Method**: tools/call
- **Arguments**:
  - tool_id: ID of tool to add
  - transport: "http-only" (default)
- **Returns**: Raw response text with configuration result

## Important Notes

1. All tools use the same base endpoint: https://mcpsearchtool.com/mcp
2. All tools use JSON-RPC 2.0 protocol
3. All tools are decorated with both `@staticmethod` and `@tool`
4. All tools return raw response text for agents to parse
5. All tools use the `tools/call` method with specific tool names

## Example Usage

```python
# Search for tools
result = search_tools("automation testing")

# Get details of a specific tool
details = get_tool_detail("tool-123")

# Add tool to configuration
config = add_mcp_tool("tool-123")
```

## Common Headers
```python
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

## Error Handling
All tools catch exceptions and return formatted error messages:
- Search: "Search failed: {error}"
- Details: "Tool detail lookup failed: {error}"
- Add: "Tool addition failed: {error}" 