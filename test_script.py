import asyncio
import os
import uuid
import logging
import base64
from typing import Optional, List, Dict
import json

import httpx
from litellm import completion
import weave

weave.init("wv_mcp")

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP Configuration
MCP_SERVICE_URL = "https://mcpsearchtool.com/mcp"
MODEL_NAME = "gpt-4o-mini"
MCP_VERSION = "2024-11-05"  # Using the most recent stable version

# Standard headers for MCP protocol
MCP_HEADERS = {
    "MCP-Protocol-Version": MCP_VERSION,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class MCPClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session_id = None
        self.client = httpx.AsyncClient(timeout=30)
    
    async def initialize(self) -> bool:
        """Initialize connection with MCP server"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "initialize",
                "params": {
                    "protocol_version": MCP_VERSION
                }
            }
            
            response = await self.client.post(
                self.base_url,
                json=payload,
                headers=MCP_HEADERS
            )
            response.raise_for_status()
            
            # Get and store session ID from headers
            self.session_id = response.headers.get("Mcp-Session-Id")
            if not self.session_id:
                logger.error("No session ID received from server")
                return False
                
            logger.info(f"Successfully initialized MCP connection. Session ID: {self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP connection: {e}")
            return False

    async def list_tools(self) -> Optional[Dict]:
        """List all available MCP tools using tools/list method"""
        if not self.session_id:
            logger.error("No active session. Call initialize() first")
            return None
            
        try:
            headers = {
                **MCP_HEADERS,
                "Mcp-Session-Id": self.session_id
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/list"
            }
            
            logger.debug(f"Sending tools/list request: {payload}")
            response = await self.client.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                logger.error(f"MCP error: {data['error']}")
                return None
                
            if "result" in data and "tools" in data["result"]:
                logger.debug(f"Got tools list: {data}")
                return data["result"]["tools"]
            
            return None
            
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return None
    
    async def search_tools(self, query: str) -> Optional[Dict]:
        """Search for tools using natural language query"""
        if not self.session_id:
            logger.error("No active session. Call initialize() first")
            return None
            
        try:
            headers = {
                **MCP_HEADERS,
                "Mcp-Session-Id": self.session_id
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",  # Changed back to tools/call
                "params": {
                    "name": "search_tools",  # Specify the tool name
                    "arguments": {  # Wrap arguments in an arguments object
                        "query": query,
                        "max_results": 5
                    }
                }
            }
            
            logger.debug(f"Sending search request: {payload}")
            response = await self.client.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            # Better response handling
            if "error" in data:
                logger.error(f"MCP error: {data['error']}")
                return None
                
            if "result" in data:
                logger.debug(f"Got response: {data}")
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error searching tools: {e}")
            return None

    async def get_tool_detail(self, tool_id: str) -> Optional[Dict]:
        """Get detailed information about a specific tool"""
        if not self.session_id:
            logger.error("No active session. Call initialize() first")
            return None
            
        try:
            headers = {
                **MCP_HEADERS,
                "Mcp-Session-Id": self.session_id
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "get_tool_detail",
                    "arguments": {
                        "tool_id": tool_id
                    }
                }
            }
            
            logger.debug(f"Sending tool detail request: {payload}")
            response = await self.client.post(
                self.base_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                logger.error(f"MCP error: {data['error']}")
                return None
                
            if "result" in data:
                logger.debug(f"Got tool details: {data}")
                return data
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting tool details: {e}")
            return None
    
    async def close(self):
        """Close the client connection"""
        await self.client.aclose()

async def main():
    # Initialize MCP client
    mcp_client = MCPClient(MCP_SERVICE_URL)
    
    try:
        # Initialize connection
        if not await mcp_client.initialize():
            logger.error("Failed to initialize MCP connection. Exiting.")
            return
            
        # List available tools first
        print("\nFetching available MCP tools...")
        tools = await mcp_client.list_tools()
        if not tools:
            print("\nCouldn't fetch available tools")
            return
            
        # Store tools for later use
        available_tools = tools
        # Keep track of tools found in searches
        searched_tools = []
            
        # Display tools with details
        print("\nAvailable MCP Tools:")
        for tool in tools:
            print(f"\nName: {tool.get('name')}")
            if tool.get('description'):
                print(f"Description: {tool.get('description')}")
            if tool.get('inputSchema'):
                print("Input Schema:")
                for param_name, param_info in tool['inputSchema'].get('properties', {}).items():
                    required = "required" if param_name in tool['inputSchema'].get('required', []) else "optional"
                    default = f", default: {param_info['default']}" if 'default' in param_info else ""
                    print(f"  - {param_name} ({param_info.get('type', 'any')}, {required}{default})")
                    if param_info.get('description'):
                        print(f"    {param_info['description']}")
            print("-" * 50)
            
        # Main interaction loop
        while True:
            try:
                print("\nSelect a tool to use:")
                for i, tool in enumerate(available_tools, 1):
                    print(f"{i}. {tool['name']} - {tool.get('description', 'No description')}")
                print("0. Exit")
                
                choice = input("\nEnter tool number: ").strip()
                if choice == "0":
                    break
                    
                try:
                    tool_index = int(choice) - 1
                    if 0 <= tool_index < len(available_tools):
                        selected_tool = available_tools[tool_index]
                        print(f"\nSelected tool: {selected_tool['name']}")
                        
                        # Handle tool-specific input
                        if selected_tool['name'] == 'search_tools':
                            query = input("\nEnter your search query: ")
                            response = await mcp_client.search_tools(query)
                            if response and 'result' in response:
                                content = response['result']['content'][0]['text']
                                search_results = json.loads(content)
                                
                                # Clear previous search results
                                searched_tools.clear()
                                
                                print(f"\nFound {search_results['total_found']} tools:")
                                for result in search_results['results']:
                                    tool = result['tool']
                                    # Add to searched tools list
                                    searched_tools.append(tool)
                                    print(f"\nName: {tool['name']}")
                                    print(f"ID: {tool['id']}")
                                    print(f"Score: {result['score']}")
                                    if tool['description']:
                                        print(f"Description: {tool['description']}")
                                    if tool['endpoints']:
                                        print(f"Endpoints: {', '.join(tool['endpoints'])}")
                                    print("-" * 50)
                            else:
                                print("\nNo tools found matching your query")
                                
                        elif selected_tool['name'] == 'get_tool_detail':
                            if not searched_tools:
                                print("\nNo tools available. Please search for tools first.")
                                continue
                                
                            print("\nSelect a tool to get details for:")
                            for i, tool in enumerate(searched_tools, 1):
                                print(f"{i}. {tool['name']} (ID: {tool['id']})")
                            
                            tool_choice = input("\nEnter tool number: ").strip()
                            try:
                                tool_index = int(tool_choice) - 1
                                if 0 <= tool_index < len(searched_tools):
                                    tool_id = searched_tools[tool_index]['id']
                                    response = await mcp_client.get_tool_detail(tool_id)
                                    
                                    if response and 'result' in response:
                                        tool = response['result']
                                        print("\nTool Details:")
                                        print(f"Name: {tool['name']}")
                                        print(f"ID: {tool['id']}")
                                        if tool.get('description'):
                                            print(f"Description: {tool['description']}")
                                        if tool.get('endpoints'):
                                            print(f"Endpoints: {', '.join(tool['endpoints'])}")
                                        if tool.get('input_schema'):
                                            print("\nInput Schema:")
                                            print(json.dumps(tool['input_schema'], indent=2))
                                        print("-" * 50)
                                    else:
                                        print("\nCouldn't fetch tool details")
                                else:
                                    print("\nInvalid tool number")
                            except ValueError:
                                print("\nPlease enter a valid number")
                        else:
                            print(f"\nSupport for {selected_tool['name']} not yet implemented")
                    else:
                        print("\nInvalid tool number")
                except ValueError:
                    print("\nPlease enter a valid number")
                    
            except Exception as e:
                logger.error(f"Error: {e}")
    
    finally:
        # Ensure we close the client properly
        await mcp_client.close()

if __name__ == "__main__":
    asyncio.run(main())
