import json
import os
import logging
from typing import Dict, Optional
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigAgent:
    """A2A agent for managing MCP tool configurations"""
    
    def __init__(self, config_path: str = "mcp.json"):
        self.config_path = Path(config_path)
        self.config: Dict = self.load_config()
        
    def load_config(self) -> Dict:
        """Load the MCP configuration file or create it if it doesn't exist"""
        try:
            # Create default config
            default_config = {
                "servers": {},
                "version": "1.0.0",
                "description": "MCP tool configuration file"
            }
            
            # If file doesn't exist, create it with default config
            if not self.config_path.exists():
                logger.info(f"Creating new config file at {self.config_path}")
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
                
            # If file exists but is empty
            if self.config_path.stat().st_size == 0:
                logger.info(f"Config file is empty, initializing with default config")
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
                
            # Load existing config
            with open(self.config_path, 'r') as f:
                config = json.load(f)
                
            # Ensure required structure exists
            if "servers" not in config:
                config["servers"] = {}
            if "version" not in config:
                config["version"] = "1.0.0"
            if "description" not in config:
                config["description"] = "MCP tool configuration file"
                
            # Save normalized config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            return config
            
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in config file: {e}")
            # Backup corrupted file if it exists
            if self.config_path.exists():
                backup_path = self.config_path.with_suffix('.json.bak')
                logger.info(f"Creating backup of corrupted config at {backup_path}")
                self.config_path.rename(backup_path)
            
            # Create new config file
            default_config = {
                "servers": {},
                "version": "1.0.0",
                "description": "MCP tool configuration file"
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {
                "servers": {},
                "version": "1.0.0",
                "description": "MCP tool configuration file"
            }
            
    def save_config(self) -> bool:
        """Save the current configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
            
    def add_server(self, server_name: str, server_config: Dict) -> bool:
        """Add or update a server configuration"""
        try:
            if "servers" not in self.config:
                self.config["servers"] = {}
                
            # Update server configuration
            self.config["servers"][server_name] = {
                "command": server_config.get("command", "npx"),
                "args": server_config.get("args", []),
                "env": server_config.get("env", {})
            }
            
            return self.save_config()
        except Exception as e:
            logger.error(f"Error adding server config: {e}")
            return False
            
    def remove_server(self, server_name: str) -> bool:
        """Remove a server configuration"""
        try:
            if server_name in self.config.get("servers", {}):
                del self.config["servers"][server_name]
                return self.save_config()
            return False
        except Exception as e:
            logger.error(f"Error removing server config: {e}")
            return False
            
    def get_server(self, server_name: str) -> Optional[Dict]:
        """Get a server configuration by name"""
        return self.config.get("servers", {}).get(server_name)
        
    def list_servers(self) -> Dict:
        """List all configured servers"""
        return self.config.get("servers", {})
        
    def handle_mcp_tool_response(self, response_data: Dict) -> bool:
        """Handle the response from add_mcp_tool and update configuration"""
        try:
            if not response_data or "result" not in response_data:
                return False
                
            content = response_data["result"]["content"][0]["text"]
            config_data = json.loads(content)
            
            # Extract server configuration
            server_name = config_data["server_name"]
            server_config = config_data["config_snippet"]
            
            # Add to configuration
            return self.add_server(server_name, server_config)
            
        except Exception as e:
            logger.error(f"Error handling MCP tool response: {e}")
            return False
            
    def get_agent_card(self) -> Dict:
        """Return the agent's capabilities card"""
        return {
            "name": "MCP Config Agent",
            "description": "Manages MCP tool configurations and server settings",
            "version": "1.0.0",
            "endpoints": ["/config"],
            "capabilities": [
                "add_server",
                "remove_server",
                "list_servers",
                "get_server",
                "handle_mcp_tool_response"
            ]
        }
        
    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming A2A requests"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method == "add_server":
                success = self.add_server(
                    params["server_name"],
                    params["server_config"]
                )
                return {"success": success}
                
            elif method == "remove_server":
                success = self.remove_server(params["server_name"])
                return {"success": success}
                
            elif method == "list_servers":
                servers = self.list_servers()
                return {"servers": servers}
                
            elif method == "get_server":
                server = self.get_server(params["server_name"])
                return {"server": server}
                
            elif method == "handle_mcp_tool_response":
                success = self.handle_mcp_tool_response(params["response_data"])
                return {"success": success}
                
            else:
                return {"error": f"Unknown method: {method}"}
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {"error": str(e)} 