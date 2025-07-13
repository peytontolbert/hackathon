# Agent-to-Agent (A2A) Protocol Implementation

## Overview

The A2A protocol enables autonomous agents to discover, communicate, and collaborate with each other. This document details our implementation of the A2A protocol within the MCP client framework.

## Agent Card Specification

Every A2A agent must expose an agent card at `/.well-known/agent.json`:

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

## Communication Protocol

### Message Format

All A2A messages use JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": "uuid-string",
  "method": "method_name",
  "params": {
    // method-specific parameters
  }
}
```

### Standard Methods

1. `discover`
   - Purpose: Agent discovery and capability querying
   - Returns: Agent card information

2. `tasks/send`
   - Purpose: Send task to agent
   - Parameters: Task description and requirements

3. `status`
   - Purpose: Check agent health and availability
   - Returns: Current agent status

## Agent Discovery

Agents are discovered through port scanning:
1. Scan ports 1000-1010
2. Request `/.well-known/agent.json` from each port
3. Parse and validate agent cards
4. Register discovered agents

## Implementation Example

```python
async def discover_agents(host: str = "localhost", 
                        start_port: int = 1000,
                        end_port: int = 1010) -> List[Dict]:
    """Discover available A2A agents"""
    agents = []
    for port in range(start_port, end_port + 1):
        try:
            url = f"http://{host}:{port}/.well-known/agent.json"
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code == 200:
                    agent_card = response.json()
                    agents.append({
                        "port": port,
                        "card": agent_card
                    })
        except Exception:
            continue
    return agents
```

## Error Handling

Standard error responses follow JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": "request-id",
  "error": {
    "code": -32000,
    "message": "Error description"
  }
}
```

Common error codes:
- -32700: Parse error
- -32600: Invalid request
- -32601: Method not found
- -32602: Invalid params

## Security Considerations

1. **Authentication**
   - Optional per agent
   - Specified in agent card
   - Token-based when required

2. **Port Security**
   - Limited port range (1000-1010)
   - Local-only by default
   - Configurable host restrictions

3. **Input Validation**
   - JSON schema validation
   - Parameter type checking
   - Size limits on payloads

## Weave Integration

A2A communications are automatically traced:
1. Agent discovery spans
2. Inter-agent communication
3. Task execution tracking
4. Error and performance metrics

## Best Practices

1. **Agent Design**
   - Single responsibility principle
   - Clear capability documentation
   - Proper error handling

2. **Communication**
   - Asynchronous by default
   - Timeout handling
   - Retry mechanisms

3. **Discovery**
   - Regular rediscovery
   - Health checks
   - Capability updates

## Testing

Test scenarios should cover:
1. Agent discovery
2. Communication patterns
3. Error conditions
4. Load handling
5. Security measures 