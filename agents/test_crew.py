import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from crewai.tools import tool
import json

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables!")

class SimpleTestCrew:
    def __init__(self):
        # Create our agents
        self.researcher = self._create_researcher()
        self.evaluator = self._create_evaluator()
        self.configurator = self._create_configurator()
        
    def _create_researcher(self):
        return Agent(
            role='Tool Researcher',
            goal='Find the most relevant MCP tools based on user needs',
            backstory="""You are an expert at understanding user requirements 
            and finding appropriate tools. You excel at translating natural 
            language requests into technical requirements.""",
            tools=[SimpleTestCrew.analyze_requirements],
            verbose=False
        )
        
    def _create_evaluator(self):
        return Agent(
            role='Tool Evaluator',
            goal='Select the best tool that matches user requirements',
            backstory="""You are an expert at evaluating technical tools and 
            matching them to user needs. You understand both technical capabilities 
            and user experience considerations.""",
            tools=[SimpleTestCrew.evaluate_tool_match],
            verbose=False
        )

    def _create_configurator(self):
        return Agent(
            role='Tool Configurator',
            goal='Successfully integrate the selected tool into the user\'s environment',
            backstory="""You are an expert at tool configuration and integration. 
            You ensure tools are properly set up and ready to use.""",
            tools=[SimpleTestCrew.verify_tool_setup],
            verbose=False
        )
    
    @staticmethod
    @tool("Analyzes user requirements for tool selection")
    def analyze_requirements(query: str) -> dict:
        """
        Tool for analyzing user requirements
        
        Args:
            query (str): The user's tool request to analyze
            
        Returns:
            Dict: Analyzed requirements in JSON format
        """
        try:
            # Extract key requirements from the query
            requirements = {
                "core_functionality": query.split()[0],  # First word as main function
                "technical_requirements": [],
                "integration_needs": []
            }
            
            # Add basic technical requirements
            if "test" in query.lower():
                requirements["technical_requirements"].append("Testing framework")
            if "automat" in query.lower():
                requirements["technical_requirements"].append("Automation support")
            
            return requirements
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
        
    @staticmethod
    @tool("Evaluates how well a tool matches requirements")
    def evaluate_tool_match(tool: dict, requirements: dict) -> dict:
        """
        Tool for evaluating how well a tool matches requirements
        
        Args:
            tool (Dict): Tool details to evaluate
            requirements (Dict): Requirements to match against
            
        Returns:
            Dict: Evaluation results in JSON format
        """
        try:
            # Simple matching logic
            matches = []
            missing = []
            
            for req in requirements:
                if req.lower() in str(tool).lower():
                    matches.append(req)
                else:
                    missing.append(req)
                    
            return {
                "tool_name": tool.get("name", "Unknown"),
                "matching_requirements": matches,
                "missing_requirements": missing,
                "match_score": len(matches) / (len(matches) + len(missing))
            }
            
        except Exception as e:
            return {"error": f"Evaluation failed: {str(e)}"}

    @staticmethod
    @tool("Verifies successful tool setup")
    def verify_tool_setup(tool_id: str) -> bool:
        """
        Tool for verifying successful tool setup
        
        Args:
            tool_id (str): ID of the tool to verify
            
        Returns:
            bool: True if setup is verified, False otherwise
        """
        try:
            # Simple verification - just check if tool_id is provided
            return bool(tool_id and tool_id.strip())
        except Exception as e:
            return False
        
    def handle_tool_request(self, user_query: str):
        # Create tasks
        tasks = [
            Task(
                description=f"""Analyze this user request and find relevant MCP tools:
                "{user_query}"
                
                1. Extract key requirements and features needed
                2. Search for tools that might match
                3. Return both requirements and found tools""",
                agent=self.researcher,
                expected_output="""A JSON object containing:
                {
                    "requirements": ["list of requirements"],
                    "potential_tools": ["list of matching tools"]
                }"""
            ),
            Task(
                description=f"""Evaluate tools for this request:
                "{user_query}"
                
                1. Review available tools and their capabilities
                2. Score them against user requirements
                3. Rank them by suitability
                4. Return detailed evaluation of top 3 choices""",
                agent=self.evaluator,
                expected_output="""A JSON object containing:
                {
                    "evaluated_tools": [
                        {
                            "name": "tool name",
                            "score": "match score",
                            "strengths": ["list of strengths"],
                            "weaknesses": ["list of weaknesses"]
                        }
                    ]
                }"""
            ),
            Task(
                description=f"""Configure the best tool for:
                "{user_query}"
                
                1. Get detailed information about the selected tool
                2. Set up appropriate configuration
                3. Verify the setup was successful
                4. Return configuration results""",
                agent=self.configurator,
                expected_output="""A JSON object containing:
                {
                    "tool_name": "name of configured tool",
                    "configuration": "configuration details",
                    "verification_status": "success/failure",
                    "next_steps": ["list of any required next steps"]
                }"""
            )
        ]
        
        # Create crew
        crew = Crew(
            agents=[self.researcher, self.evaluator, self.configurator],
            tasks=tasks,
            verbose=True  # Enable verbose output
        )
        
        # Run the crew
        try:
            print("\nStarting crew execution...")
            result = crew.kickoff()
            print("\nRaw crew output:")
            print(result)
            
            # Convert CrewOutput to string and parse as JSON
            result_str = str(result)
            print("\nCrew output as string:")
            print(result_str)
            
            try:
                result_dict = json.loads(result_str)
                print("\nParsed JSON result:")
                print(json.dumps(result_dict, indent=2))
                
                # Get configuration info
                config = result_dict.get("configuration", {})
                config_features = []
                if isinstance(config, dict):
                    config_features = config.get("features", [])
                elif isinstance(config, str):
                    config_features = [config]
                
                # Get evaluator info from the second task if available
                evaluator_output = None
                for task in tasks:
                    if task.agent == self.evaluator:
                        try:
                            evaluator_result = json.loads(str(task.output))
                            evaluator_output = evaluator_result.get("evaluated_tools", [])[0]
                        except (json.JSONDecodeError, IndexError, AttributeError):
                            pass
                
                return {
                    "success": True,
                    "tool_name": result_dict.get("tool_name", "Unknown Tool"),
                    "description": config if isinstance(config, str) else ", ".join(config_features),
                    "setup_status": {
                        "status": result_dict.get("verification_status", "unknown"),
                        "environment": config.get("environment", "") if isinstance(config, dict) else "",
                        "supported_browsers": config.get("browsers_supported", []) if isinstance(config, dict) else []
                    },
                    "requirements_met": evaluator_output.get("strengths", []) if evaluator_output else config_features,
                    "requirements_missing": evaluator_output.get("weaknesses", []) if evaluator_output else [],
                    "next_steps": result_dict.get("next_steps", [])
                }
            except json.JSONDecodeError as e:
                print("\nFailed to parse JSON:")
                print(f"Error: {e}")
                # If JSON parsing fails, return the raw string result
                return {
                    "success": True,
                    "tool_name": "Unknown Tool",
                    "description": str(result),
                    "setup_status": {},
                    "requirements_met": [],
                    "requirements_missing": [],
                    "alternatives": []
                }
        except Exception as e:
            print(f"\nError during crew execution: {e}")
            return {
                "success": False,
                "message": f"Error processing request: {str(e)}"
            }

def main():
    # Create test crew
    crew = SimpleTestCrew()
    
    while True:
        query = input("\nWhat kind of tool do you need? (or 'exit' to quit): ")
        if query.lower() == 'exit':
            break
            
        try:
            print("\nProcessing your request...")
            result = crew.handle_tool_request(query)
            
            if result["success"]:
                print(f"\n✅ Successfully processed request")
                print("\nResult details:")
                for key, value in result.items():
                    if key != "success":  # Skip printing success flag
                        print(f"- {key}: {value}")
            else:
                print(f"\n❌ {result['message']}")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main() 