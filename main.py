import asyncio
import logging
from typing import Optional, Dict
import weave  # Keep import for inference
from agents.agent import MCPToolCrew
import httpx

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Weave tracing - temporarily disabled to prevent crew hanging
# weave.init("wv_mcp")

class MCPAssistant:
    """Main assistant class that coordinates between user and crew"""
    
    def __init__(self):
        self.tool_crew = MCPToolCrew()
        self.session_id = None
        
    def handle_request(self, user_input: str) -> Dict:
        """Handle user request using crew-based orchestration"""
        try:
            # Let the crew handle the entire workflow
            result = self.tool_crew.run_task(user_input)
            
            if not result:
                return {
                    "success": False,
                    "message": "No response from crew"
                }
            
            # Format the result for user display
            formatted = self._format_result(result)
            return formatted
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def _format_result(self, result: Dict) -> Dict:
        """Format crew result for user display"""
        if not isinstance(result, dict):
            return {
                "success": False,
                "message": "Invalid result format from crew"
            }
            
        # Extract task results and step logs (intermediate agent outputs)
        task_results = result.get("task_results", [])
        step_logs = result.get("step_logs", [])
        
        formatted = {
            "success": result.get("status") == "success",
            "tool_name": result.get("tool_id", "Unknown Tool"),
            "description": "Tool processed by AI agents",
            "setup_status": result.get("config_updated", False),
            "requirements_met": [],
            "requirements_missing": [],
            "alternatives": [],
            "agent_output": str(result.get("result", "")),
            "task_results": task_results,  # Individual task results from each agent
            "step_logs": step_logs  # Intermediate step logs during execution
        }
        
        if not formatted["success"]:
            formatted["message"] = result.get("error", "Unknown error occurred")
            
        return formatted

def display_menu():
    """Display interactive menu"""
    print("\n=== MCP Tool Assistant ===")
    print("1. Search and configure a tool")
    print("2. View configured tools")
    print("3. Help")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    return choice

def handle_tool_search(assistant: MCPAssistant):
    """Handle tool search and configuration workflow"""
    query = input("\nWhat kind of tool are you looking for? Describe your needs: ")
    
    print("\nProcessing your request...")
    result = assistant.handle_request(query)
    
    if result["success"]:
        print("\n✅ Tool Configuration Success!")
        print(f"\nConfigured Tool: {result['tool_name']}")
        print(f"Description: {result['description']}")
        
        print("\nRequirements Met:")
        for req in result["requirements_met"]:
            print(f"✓ {req}")
            
        if result["requirements_missing"]:
            print("\nRequirements Not Met:")
            for req in result["requirements_missing"]:
                print(f"✗ {req}")
                
        if result.get("alternatives"):
            print("\nAlternative Tools:")
            for alt in result["alternatives"][:3]:
                print(f"- {alt['name']}: {alt['match_score']}% match")
    else:
        print(f"\n❌ {result['message']}")
        
        if result.get("alternatives"):
            print("\nSuggested Alternatives:")
            for alt in result["alternatives"][:3]:
                print(f"- {alt['name']}: {alt['description']}")

def view_configured_tools(assistant: MCPAssistant):
    """Display currently configured tools"""
    print("\nFetching configured tools...")
    # TODO: Implement viewing configured tools
    print("Feature coming soon!")

def show_help():
    """Display help information"""
    print("\n=== MCP Tool Assistant Help ===")
    print("This assistant helps you find and configure MCP tools using AI agents.")
    print("\nHow to use:")
    print("1. Search for tools: Describe what you need in natural language")
    print("2. View tools: See what tools are already configured")
    print("3. The AI agents will:")
    print("   - Analyze your requirements")
    print("   - Search for matching tools")
    print("   - Evaluate the best options")
    print("   - Handle configuration automatically")
    print("\nTips:")
    print("- Be specific about your requirements")
    print("- Include any technical constraints")
    print("- Mention integration needs")

def main():
    """Main application loop"""
    assistant = MCPAssistant()
    
    while True:
        choice = display_menu()
        
        try:
            if choice == "1":
                handle_tool_search(assistant)
            elif choice == "2":
                view_configured_tools(assistant)
            elif choice == "3":
                show_help()
            elif choice == "4":
                print("\nThank you for using MCP Tool Assistant!")
                break
            else:
                print("\nInvalid choice. Please try again.")
                
            input("\nPress Enter to continue...")
            
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            print(f"\nAn error occurred: {e}")
            print("Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\nFatal error occurred: {e}")