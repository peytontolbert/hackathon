# Search Hackathon Project Architecture

This diagram shows the overall architecture and relationships between components in the search hackathon project.

```mermaid
graph TD
    subgraph "MCP Client with A2A Integration"
        A[main.py<br/>Entry Point] --> B[server.py<br/>Web Interface]
        A --> C[config_agent.py<br/>Agent Configuration]
        A --> D[config_server.py<br/>Server Configuration]
        A --> E[agent.py<br/>Core Agent Logic]
        
        subgraph "Configuration"
            C --> F[mcp.json<br/>MCP Tools Config]
            D --> G[Environment Variables<br/>API Keys & Settings]
        end
        
        subgraph "Core Functions"
            E --> H[A2A Discovery<br/>Agent-to-Agent Protocol]
            E --> I[MCP Client<br/>Tool Management]
            E --> J[Weave Tracing<br/>Observability]
            E --> K[CrewAI Integration<br/>Multi-Agent Coordination]
        end
        
        B --> L[templates/index.html<br/>Web UI]
        
        %% Main connections
        C --> E
        D --> B
        F --> E
        G --> E
        
        %% Function interactions
        H --> I
        I --> J
        K --> H
    end
    
    style A fill:#e1f5fe
    style E fill:#fff3e0
    style C fill:#e8f5e8
    style D fill:#e8f5e8
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style J fill:#f3e5f5
    style K fill:#f3e5f5
```

## Key Components:

### Core Application
- **main.py**: Central orchestrator and entry point - coordinates all system components
- **agent.py**: Core agent functionality with A2A discovery, MCP client, Weave tracing, and CrewAI integration
- **server.py**: Web server handling HTTP requests and serving templates

### Configuration Management
- **config_agent.py**: Agent configuration management - handles agent settings and capabilities
- **config_server.py**: Server configuration management - manages web interface and API settings
- **mcp.json**: MCP tools configuration - defines available tools and their endpoints

### Core Functions (within agent.py)
- **A2A Discovery**: Agent-to-Agent protocol for dynamic agent discovery (ports 1000-1010)
- **MCP Client**: Tool management and Model Context Protocol implementation
- **Weave Tracing**: Observability and performance monitoring for all operations
- **CrewAI Integration**: Multi-agent coordination and task orchestration

## Architecture Flow:
1. The main application (`main.py`) serves as the central orchestrator
2. It connects to both the server (`server.py`) and agent systems
3. MCP tools are configured to work with the agents through `mcp.json`
4. The server provides a web interface using HTML templates
5. Comprehensive testing suite ensures functionality across all components
6. Documentation provides guidance for each major component and integration 