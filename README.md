# MCP Client with A2A Integration

## Overview
This Python-based MCP (Model Control Protocol) client provides a robust interface for interacting with MCP services while incorporating A2A (Agent-to-Agent) protocol support and Weave observability.

## Features

### MCP Protocol Support
- Full MCP 2024-11-05 protocol implementation
- Session management and initialization
- Tool discovery and search capabilities
- Detailed tool information retrieval
- Tool configuration management

### A2A Integration
- Dynamic agent discovery (ports 1000-1010)
- Agent card fetching from well-known endpoints
- LLM-powered agent routing
- Conversation history management
- Multi-agent task coordination

### Weave Observability
- Automatic MCP call tracing
- Custom operation spans
- Performance metrics
- Error tracking
- Agent interaction visualization

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Required for LLM-based agent routing
- `ANTHROPIC_API_KEY`: Optional for Claude-based tools
- `WEAVE_PROJECT`: Defaults to "wv_mcp"

### MCP Settings
- Protocol Version: 2024-11-05
- Default Service URL: https://mcpsearchtool.com/mcp
- Default Transport: http-only

### A2A Configuration
- Host: localhost
- Port Range: 1000-1010
- Agent Card Path: /.well-known/agent.json
- Default Model: openai/gpt-4o-mini

## Usage

### Basic MCP Operations

1. Initialize Client:
   - Create MCPClient instance
   - Initialize connection
   - Verify session establishment

2. Tool Management:
   - List available tools
   - Search tools by natural language
   - Get detailed tool information
   - Add tools to configuration

3. A2A Integration:
   - Discover available agents
   - Route requests to appropriate agents
   - Handle agent responses
   - Maintain conversation context

### Advanced Features

1. Media Handling:
   - Text processing
   - Image support (PNG, JPEG)
   - File attachments
   - Binary data handling

2. Error Management:
   - Comprehensive error tracking
   - Automatic retries
   - Fallback mechanisms
   - Error reporting via Weave

3. Observability:
   - Request tracing
   - Performance monitoring
   - Error tracking
   - Agent interaction analysis

## Error Handling

### Common Errors
- Connection failures
- Authentication issues
- Invalid tool configurations
- Agent discovery problems
- Routing failures

### Recovery Strategies
- Automatic session renewal
- Connection retries
- Agent failover
- Graceful degradation
- User feedback

## Development

### Requirements
- Python 3.8+
- httpx
- litellm
- weave-python
- FastMCP

### Testing
- Unit tests for core functionality
- Integration tests for A2A
- Performance benchmarks
- Error scenario validation

## Best Practices

1. Session Management:
   - Initialize before operations
   - Handle session expiry
   - Clean up resources

2. Tool Usage:
   - Validate tool availability
   - Check input schemas
   - Handle response formats
   - Monitor performance

3. A2A Integration:
   - Regular agent discovery
   - Validate agent capabilities
   - Monitor agent health
   - Handle timeouts

4. Observability:
   - Enable appropriate logging
   - Monitor key metrics
   - Track error rates
   - Analyze performance

## Contributing

### Guidelines
1. Follow PEP 8 style guide
2. Add tests for new features
3. Update documentation
4. Maintain backward compatibility

### Development Process
1. Fork repository
2. Create feature branch
3. Implement changes
4. Add tests
5. Submit pull request

## License
MIT License - See LICENSE file for details

## Support
- GitHub Issues
- Documentation
- Community Forums
- Email Support

