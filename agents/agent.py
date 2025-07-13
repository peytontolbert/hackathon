import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import json
import httpx
import uuid
import logging
from typing import Optional, Dict

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables!")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP Configuration
MCP_SERVICE_URL = "https://mcpsearchtool.com/mcp"
MCP_VERSION = "2024-11-05"
MCP_HEADERS = {
    "MCP-Protocol-Version": MCP_VERSION,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class MCPClient:
    def __init__(self):
        self.base_url = MCP_SERVICE_URL
        self.session_id = None
        self.client = httpx.Client(timeout=30.0)
        
    def initialize(self) -> bool:
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
            
            response = self.client.post(
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

class MCPToolCrew:
    """CrewAI implementation for MCP tool orchestration"""
    
    # Class variable to store the MCP client
    _mcp_client = None
    
    def __init__(self):
        # Initialize LLM
        self.llm = LLM(
            model="openai/meta-llama/Llama-4-Scout-17B-16E-Instruct",
            api_base="https://api.inference.wandb.ai/v1",
            api_key=os.getenv("WANDB_API_KEY"),
            extra_headers={"OpenAI-Project": "peytontolbert-ai/mcp-search"}
        )
        
        # Initialize MCP client as class variable
        if MCPToolCrew._mcp_client is None:
            MCPToolCrew._mcp_client = MCPClient()
            if not MCPToolCrew._mcp_client.initialize():
                raise RuntimeError("Failed to initialize MCP connection")
        
        # Create our agents
        self.researcher = self._create_researcher()
        self.evaluator = self._create_evaluator()
        self.configurator = self._create_configurator()

    @staticmethod
    @tool("Search MCP tools")
    def search_tools(query: str) -> str:
        """Search for tools using natural language query"""
        try:
            if not MCPToolCrew._mcp_client or not MCPToolCrew._mcp_client.session_id:
                return "Error: No active MCP session"
                
            headers = {
                **MCP_HEADERS,
                "Mcp-Session-Id": MCPToolCrew._mcp_client.session_id
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "search_tools",
                    "arguments": {
                        "query": query,
                        "max_results": 5
                    }
                }
            }
            
            response = httpx.post(
                MCP_SERVICE_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                return f"Error: {data['error']}"
                
            if "result" in data:
                # Handle both direct result and content-wrapped result
                if "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    results = json.loads(content)
                else:
                    results = data["result"]
                return json.dumps(results, indent=2)
            
            return "No results found"
            
        except Exception as e:
            return f"Search failed: {str(e)}"

    @staticmethod
    @tool("Get tool details")
    def get_tool_detail(tool_id: str) -> str:
        """Get detailed information about a specific tool"""
        try:
            if not MCPToolCrew._mcp_client or not MCPToolCrew._mcp_client.session_id:
                return "Error: No active MCP session"
                
            headers = {
                **MCP_HEADERS,
                "Mcp-Session-Id": MCPToolCrew._mcp_client.session_id
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
            
            response = httpx.post(
                MCP_SERVICE_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                return f"Error: {data['error']}"
                
            if "result" in data:
                # Handle both direct result and content-wrapped result
                if "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    tool_details = json.loads(content)
                else:
                    tool_details = data["result"]
                return json.dumps(tool_details, indent=2)
            
            return "Tool details not found"
            
        except Exception as e:
            return f"Tool detail lookup failed: {str(e)}"

    @staticmethod
    @tool("Add MCP tool")
    def add_mcp_tool(tool_id: str) -> str:
        """Add an MCP tool to configuration"""
        try:
            # Handle case where input is a JSON string
            if tool_id.startswith('"') and tool_id.endswith('"'):
                try:
                    parsed = json.loads(tool_id)
                    tool_id = parsed["tool_id"]
                except (json.JSONDecodeError, KeyError):
                    pass

            if not MCPToolCrew._mcp_client or not MCPToolCrew._mcp_client.session_id:
                return json.dumps({
                    "status": "failed",
                    "error": "No active MCP session"
                })
                
            headers = {
                **MCP_HEADERS,
                "Mcp-Session-Id": MCPToolCrew._mcp_client.session_id
            }
            
            # Prepare arguments with required fields
            arguments = {
                "tool_id": tool_id,
                "transport": "http-only",
                "debug": False
            }
            
            payload = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tools/call",
                "params": {
                    "name": "add_mcp_tool",
                    "arguments": arguments
                }
            }
            
            response = httpx.post(
                MCP_SERVICE_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            if "error" in data:
                return json.dumps({
                    "status": "failed",
                    "error": data["error"]
                })
                
            if "result" in data:
                # Extract content from result
                if "content" in data["result"]:
                    content = data["result"]["content"][0]["text"]
                    result = json.loads(content)
                else:
                    result = data["result"]
                
                # Call config agent to update mcp.json
                config_response = httpx.post(
                    "http://localhost:1001",
                    json={
                        "jsonrpc": "2.0",
                        "id": str(uuid.uuid4()),
                        "method": "handle_mcp_tool_response",
                        "params": {"response_data": data}
                    }
                ).json()
                
                if config_response and config_response.get("success"):
                    logger.info("Successfully updated mcp.json configuration")
                    return json.dumps({
                        "status": "success",
                        "tool_id": tool_id,
                        "config_updated": True,
                        "result": result
                    })
                else:
                    logger.warning("Failed to update mcp.json configuration")
                    return json.dumps({
                        "status": "partial_success",
                        "tool_id": tool_id,
                        "config_updated": False,
                        "result": result
                    })
            
            return json.dumps({
                "status": "failed",
                "error": "No result returned from server"
            })
            
        except Exception as e:
            logger.error(f"Tool addition failed: {e}")
            return json.dumps({
                "status": "failed",
                "error": str(e)
            })

    def _create_researcher(self):
        return Agent(
            role='Tool Researcher',
            goal='Find relevant MCP tools',
            backstory="""You are an expert at finding the right tools for any task.
            You understand user requirements and can find matching tools.""",
            llm=self.llm,
            tools=[MCPToolCrew.search_tools],
            verbose=True
        )
        
    def _create_evaluator(self):
        return Agent(
            role='Tool Evaluator',
            goal='Evaluate and select the best tool',
            backstory="""You are an expert at evaluating tools and selecting the best one.
            You look at tool details and match them to requirements.""",
            llm=self.llm,
            tools=[MCPToolCrew.get_tool_detail],
            verbose=True
        )

    def _create_configurator(self):
        return Agent(
            role='Tool Configurator',
            goal='Configure and add the selected tool',
            backstory="""You are an expert at tool configuration and integration.
            You ensure tools are properly added to the system.""",
            llm=self.llm,
            tools=[MCPToolCrew.add_mcp_tool],
            verbose=True
        )

    def run_task(self, query: str) -> dict:
        """Process a user's tool request using the crew"""
        try:
            # Create tasks in sequence
            tasks = [
                Task(
                    description=f"""Search for tools matching this request: "{query}"
                    1. Use natural language search
                    2. Consider key requirements
                    3. Return list of potential tools""",
                    agent=self.researcher,
                    expected_output="JSON list of matching tools with their IDs and descriptions"
                ),
                Task(
                    description="""Evaluate the tools found by the researcher:
                    1. Get detailed information for each tool
                    2. Compare capabilities against requirements
                    3. Select the best matching tool""",
                    agent=self.evaluator,
                    expected_output="JSON with selected tool's ID and evaluation details"
                ),
                Task(
                    description="""Configure the selected tool:
                    1. Add the tool using its ID
                    2. Use http-only transport
                    3. Verify successful addition""",
                    agent=self.configurator,
                    expected_output="JSON with configuration results and status"
                )
            ]
            
            # Capture intermediate steps during execution
            step_logs = []
            
            def step_callback(step):
                """Capture intermediate agent steps during execution"""
                import datetime
                step_logs.append({
                    "step_type": type(step).__name__,
                    "content": str(step),
                    "timestamp": datetime.datetime.now().isoformat()
                })
                logger.info(f"Step captured: {type(step).__name__} - {step}")
            
            # Create and run crew with step callback
            crew = Crew(
                agents=[self.researcher, self.evaluator, self.configurator],
                tasks=tasks,
                verbose=True,
                step_callback=step_callback
            )
            
            result = crew.kickoff()
            
            # Capture individual task results AFTER crew execution
            task_results = []
            for i, task in enumerate(tasks):
                # Access task output after crew.kickoff() completes
                if hasattr(task, 'output') and task.output:
                    task_result = {
                        "task_id": i + 1,
                        "agent": task.agent.role,
                        "description": task.description,
                        "expected_output": task.expected_output,
                        "output": str(task.output.raw) if task.output else "No output captured",
                        "status": "completed"
                    }
                else:
                    task_result = {
                        "task_id": i + 1,
                        "agent": task.agent.role,
                        "description": task.description,
                        "expected_output": task.expected_output,
                        "output": "Task output not available",
                        "status": "failed"
                    }
                task_results.append(task_result)
            
            # Convert CrewOutput to string and parse as JSON
            result_str = str(result)
            try:
                result_dict = json.loads(result_str)
            except json.JSONDecodeError:
                # If not valid JSON, create a standard format
                result_dict = {
                    "status": "success",
                    "message": result_str
                }
            
            # Return standardized format with task results and step logs
            return {
                "status": result_dict.get("status", "success"),
                "tool_id": result_dict.get("tool_id"),
                "config_updated": result_dict.get("config_updated", False),
                "result": result_dict,
                "task_results": task_results,  # Individual task results
                "step_logs": step_logs,  # Intermediate step logs
                "error": result_dict.get("error")
            }
            
        except Exception as e:
            logger.error(f"Task failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

def main():
    # Create crew instance
    crew = MCPToolCrew()
    
    # Test query
    query = "Tell me about test automation tools"
    
    try:
        print("\nStarting crew task...")
        result = crew.run_task(query)
        print("\nResults:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main() 