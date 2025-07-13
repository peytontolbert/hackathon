# Config Agent Documentation

## Overview

The Config Agent is an A2A-compliant agent responsible for managing MCP tool configurations. It handles the storage, retrieval, and updating of MCP tool configurations in the `mcp.json` file.

## Agent Card

```json
{
  "protocol_version": "1.0",
  "name": "Config Agent",
  "description": "Manages MCP tool configurations",
  "capabilities": [
    "config_management",
    "file_operations"
  ],
  "endpoints": {
    "base": "/",
    "well_known": "/.well-known/agent.json"
  },
  "authentication": {
    "required": false
  }
}
```

## Supported Methods

### 1. `handle_mcp_tool_response`

Handles the response from MCP's `add_mcp_tool` and updates the configuration.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "uuid-string",
  "method": "handle_mcp_tool_response",
  "params": {
    "response_data": {
      "config_snippet": {
        "args": ["mcp-remote", "endpoint", "--transport", "http-only"],
        "command": "npx",
        "env": {},
        "server_name": "Tool Name"
      }
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": "uuid-string",
  "result": {
    "success": true,
    "message": "Configuration updated successfully"
  }
}
```

### 2. `get_config`

Retrieves current configuration for a specific tool or all tools.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "uuid-string",
  "method": "get_config",
  "params": {
    "server_name": "optional-tool-name"
  }
}
```

### 3. `remove_tool`

Removes a tool configuration.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": "uuid-string",
  "method": "remove_tool",
  "params": {
    "server_name": "tool-name"
  }
}
```

## Implementation Details

### Configuration File Structure

The `mcp.json` file follows this structure:
```json
{
  "version": "1.0.0",
  "servers": {
    "server-name": {
      "command": "string",
      "args": ["string"],
      "env": {},
      "transport": "string"
    }
  }
}
```

### Error Handling

The agent handles several error cases:
1. File not found
2. Invalid JSON
3. Schema validation failures
4. Concurrent access

### Weave Integration

All operations are traced:
1. Configuration updates
2. File operations
3. Validation steps
4. Error conditions

## Usage Example

```python
# Using the Config Agent from MCP client
async def add_mcp_tool(self, tool_id: str) -> Optional[Dict]:
    # Get tool config from MCP service
    mcp_response = await self.get_tool_config(tool_id)
    
    # Send to Config Agent
    config_response = await self._call_config_agent(
        "handle_mcp_tool_response",
        {"response_data": mcp_response}
    )
    
    return config_response
```

## Security

1. **File Operations**
   - Safe file handling
   - Backup creation
   - Atomic writes

2. **Input Validation**
   - Schema validation
   - Type checking
   - Size limits

3. **Access Control**
   - Local-only by default
   - Optional authentication
   - Rate limiting

## Testing

Test cases cover:
1. Configuration updates
2. File operations
3. Error handling
4. Concurrent access
5. Schema validation

## Deployment

The Config Agent runs on port 1001 and can be started with:
```bash
python config_server.py
```

## Monitoring

Monitor the agent through:
1. Weave traces
2. Log output
3. Status endpoint
4. Health checks 

# CrewAI Implementation Guide

## Core Implementation Patterns from test_crew.py

### 1. Tool Definition Pattern
```python
@staticmethod
@tool("Human readable tool name")
def tool_name(param: type) -> return_type:
    """
    Docstring with clear description
    
    Args:
        param (type): Parameter description
        
    Returns:
        return_type: Return value description
    """
    return result
```

#### Critical Requirements:
- Use `@staticmethod` decorator FIRST
- Then use `@tool("description")` decorator
- Clear docstring with Args and Returns
- Type hints for all parameters and return values
- Keep tools simple and focused

### 2. Agent Creation Pattern
```python
def _create_agent(self):
    return Agent(
        role='Clear Role Name',
        goal='Specific Goal',
        backstory="""Detailed backstory that explains the agent's
        expertise and responsibilities.""",
        llm=self.llm,  # Pass configured LLM
        tools=[self.tool_name],  # Pass tool references
        verbose=True
    )
```

#### Critical Requirements:
- Create agents in separate methods for clarity
- Use descriptive role names and goals
- Write detailed backstories
- Pass configured LLM instance
- Pass tool references directly
- Enable verbose mode during development

### 3. Crew Setup Pattern
```python
class TestCrew:
    def __init__(self):
        # 1. Configure LLM first
        self.llm = LLM(model="model_name", temperature=0)
        
        # 2. Create agents
        self.agent1 = self._create_agent1()
        self.agent2 = self._create_agent2()
        
    def run_task(self, input_data):
        # 3. Create ordered tasks
        tasks = [
            Task(
                description="Clear task description",
                agent=self.agent1,
                expected_output="Expected output format"
            )
        ]
        
        # 4. Create crew with all agents
        crew = Crew(
            agents=[self.agent1, self.agent2],
            tasks=tasks,
            verbose=True
        )
        
        # 5. Run and return results
        result = crew.kickoff()
        return result
```

#### Critical Requirements:
- Initialize LLM first in constructor
- Create agents after LLM configuration
- Create tasks with clear descriptions
- Specify expected output formats
- Include all agents in crew
- Enable verbose mode for debugging

### 4. Error Handling Pattern
```python
def main():
    try:
        # 1. Create crew instance
        crew = TestCrew()
        
        # 2. Run with test input
        result = crew.run_task("test input")
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")
```

#### Critical Requirements:
- Wrap crew operations in try/except
- Handle exceptions gracefully
- Print useful error messages
- Clean up resources properly

### 5. Tool Implementation Best Practices

1. **Keep Tools Simple**
   ```python
   @staticmethod
   @tool("Search tool")
   def search_tool(query: str) -> str:
       return f"Result for: {query}"
   ```
   - One clear responsibility
   - Simple input/output types
   - Clear error handling

2. **Tool Dependencies**
   ```python
   def __init__(self):
       self.dependency = setup_dependency()
       self.agent = Agent(
           tools=[self.tool_with_dependency]
       )
   
   @staticmethod
   @tool("Tool using dependency")
   def tool_with_dependency(input: str) -> str:
       # Access via self
       return self.dependency.process(input)
   ```
   - Initialize dependencies in constructor
   - Access via self in tools
   - Handle dependency errors

### 6. Common Mistakes to Avoid

1. **Decorator Order**
   ```python
   # WRONG
   @tool("description")
   @staticmethod
   def wrong_tool(): pass
   
   # RIGHT
   @staticmethod
   @tool("description")
   def correct_tool(): pass
   ```

2. **Tool References**
   ```python
   # WRONG
   tools=[search_tool]  # Direct function reference
   
   # RIGHT
   tools=[self.search_tool]  # Method reference
   ```

3. **Agent Configuration**
   ```python
   # WRONG
   Agent(tools=my_tools)  # List of functions
   
   # RIGHT
   Agent(tools=[self.tool1, self.tool2])  # List of bound methods
   ```

4. **Task Definition**
   ```python
   # WRONG
   Task(description="Do something")
   
   # RIGHT
   Task(
       description="Specific task description",
       agent=self.specific_agent,
       expected_output="Expected format"
   )
   ```

### 7. Testing and Debugging

1. **Enable Verbose Mode**
   ```python
   Agent(verbose=True)
   Crew(verbose=True)
   ```
   - Shows tool calls
   - Shows agent thinking
   - Shows task progress

2. **Test Tools Independently**
   ```python
   def test_tool():
       crew = TestCrew()
       result = crew.search_tool("test")
       assert "Result" in result
   ```
   - Test each tool separately
   - Verify tool dependencies
   - Check error handling

3. **Test Agent Interactions**
   ```python
   def test_crew():
       crew = TestCrew()
       result = crew.run_task("test")
       assert result is not None
   ```
   - Test complete workflows
   - Verify agent cooperation
   - Check task completion

### 8. Production Considerations

1. **Environment Setup**
   ```python
   load_dotenv()
   if not os.getenv("OPENAI_API_KEY"):
       raise ValueError("API key missing")
   ```
   - Load environment variables
   - Validate required keys
   - Handle missing configs

2. **Resource Management**
   ```python
   def __init__(self):
       self.resources = setup_resources()
   
   def cleanup(self):
       self.resources.close()
   ```
   - Initialize resources properly
   - Clean up when done
   - Handle resource errors

3. **Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)
   ```
   - Configure logging
   - Log important events
   - Track errors properly

### 9. Example Complete Implementation

```python
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import logging

# Setup
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkingCrew:
    def __init__(self):
        # 1. Validate environment
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("API key required")
            
        # 2. Configure LLM
        self.llm = LLM(
            model="gpt-4o-mini",
            temperature=0
        )
        
        # 3. Create agents
        self.agent1 = self._create_agent1()
        self.agent2 = self._create_agent2()
        
    def _create_agent1(self):
        return Agent(
            role='Role 1',
            goal='Goal 1',
            backstory="Detailed backstory 1",
            llm=self.llm,
            tools=[self.tool1],
            verbose=True
        )
        
    @staticmethod
    @tool("Tool 1")
    def tool1(input: str) -> str:
        """Tool 1 documentation"""
        try:
            return f"Result: {input}"
        except Exception as e:
            logger.error(f"Tool 1 error: {e}")
            return f"Error: {str(e)}"
            
    def run_task(self, input_data: str) -> str:
        try:
            # 1. Create tasks
            tasks = [
                Task(
                    description=f"Process: {input_data}",
                    agent=self.agent1,
                    expected_output="Expected format"
                )
            ]
            
            # 2. Create crew
            crew = Crew(
                agents=[self.agent1, self.agent2],
                tasks=tasks,
                verbose=True
            )
            
            # 3. Run
            return crew.kickoff()
            
        except Exception as e:
            logger.error(f"Task error: {e}")
            raise
```

### 10. Key Success Factors

1. **Proper Tool Definition**
   - Use both decorators in correct order
   - Include complete documentation
   - Handle errors properly

2. **Clean Agent Setup**
   - Configure LLM first
   - Create agents methodically
   - Pass correct tool references

3. **Clear Task Structure**
   - Define specific tasks
   - Assign appropriate agents
   - Specify expected outputs

4. **Error Handling**
   - Handle tool errors
   - Handle agent errors
   - Handle crew errors

5. **Resource Management**
   - Initialize properly
   - Clean up resources
   - Handle dependencies

Follow these patterns exactly to avoid common CrewAI implementation errors. 