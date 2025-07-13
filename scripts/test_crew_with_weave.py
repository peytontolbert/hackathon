import asyncio
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import os
import logging
from dotenv import load_dotenv
import weave

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Check for required API keys
if not os.getenv("WANDB_API_KEY"):
    raise ValueError("WANDB_API_KEY not found in environment variables!")

class SimpleTestCrew:
    def __init__(self):
        # Initialize with Weave inference
        try:
            self.llm = LLM(
                model="openai/meta-llama/Llama-4-Scout-17B-16E-Instruct",
                api_base="https://api.inference.wandb.ai/v1",
                api_key=os.getenv("WANDB_API_KEY"),
                extra_headers={"OpenAI-Project": "peytontolbert-ai/mcp-search"}
            )
            logger.info("Successfully initialized Weave LLM")
        except Exception as e:
            logger.error(f"Failed to initialize Weave LLM: {e}")
            raise
        
        # Create our agents
        self.researcher = self._create_researcher()
        self.analyst = self._create_analyst()
        
    def _create_researcher(self):
        return Agent(
            role='Research Specialist',
            goal='Find and collect relevant information',
            backstory="""You are an expert researcher who excels at finding 
            and collecting relevant information about any topic.""",
            llm=self.llm,
            tools=[SimpleTestCrew.search_tool],
            verbose=True
        )
        
    def _create_analyst(self):
        return Agent(
            role='Data Analyst',
            goal='Analyze and summarize information',
            backstory="""You are a skilled analyst who can process information
            and provide clear, actionable insights.""",
            llm=self.llm,
            tools=[SimpleTestCrew.analyze_tool],
            verbose=True
        )
    
    @staticmethod
    @tool("Search for information about a topic")
    def search_tool(query: str) -> str:
        """
        Search for information about a given topic
        
        Args:
            query (str): The topic to search for
            
        Returns:
            str: Information found about the topic
        """
        try:
            # Simulate search with more detailed response
            return f"Found detailed information about {query}:\n" + \
                   f"- Latest research and developments\n" + \
                   f"- Key concepts and applications\n" + \
                   f"- Current trends and future outlook"
        except Exception as e:
            logger.error(f"Error in search_tool: {e}")
            return f"Error searching for information: {str(e)}"
        
    @staticmethod
    @tool("Analyze provided information")
    def analyze_tool(data: str) -> str:
        """
        Analyze the provided information
        
        Args:
            data (str): The information to analyze
            
        Returns:
            str: Analysis results
        """
        try:
            # Simulate analysis with more structured response
            return f"Analysis results:\n" + \
                   f"1. Key findings from the data\n" + \
                   f"2. Important patterns identified\n" + \
                   f"3. Recommendations based on analysis\n" + \
                   f"Raw data: {data}"
        except Exception as e:
            logger.error(f"Error in analyze_tool: {e}")
            return f"Error analyzing information: {str(e)}"
        
    def run_test_task(self, query: str):
        try:
            # Create tasks with more specific outputs
            tasks = [
                Task(
                    description=f"""Research this topic in detail: {query}
                    1. Find latest developments
                    2. Identify key concepts
                    3. Look for current trends""",
                    agent=self.researcher,
                    expected_output="Comprehensive information with sources and key findings"
                ),
                Task(
                    description=f"""Analyze the research findings about: {query}
                    1. Extract key insights
                    2. Identify patterns
                    3. Make recommendations""",
                    agent=self.analyst,
                    expected_output="Detailed analysis with actionable insights"
                )
            ]
            
            # Create crew with verbose output
            crew = Crew(
                agents=[self.researcher, self.analyst],
                tasks=tasks,
                verbose=True
            )
            
            # Run the crew with logging
            logger.info(f"Starting crew task for query: {query}")
            result = crew.kickoff()
            logger.info("Successfully completed crew task")
            return result
            
        except Exception as e:
            logger.error(f"Error in run_test_task: {e}")
            raise

def main():
    try:
        # Create test crew
        logger.info("Initializing test crew...")
        test_crew = SimpleTestCrew()
        
        # Test queries with increasing complexity
        queries = [
            "Tell me about artificial intelligence",
            "Explain the impact of quantum computing on cryptography",
            "Describe recent advances in renewable energy technology"
        ]
        
        for query in queries:
            try:
                print(f"\nTesting with query: {query}")
                print("=" * 50)
                
                result = test_crew.run_test_task(query)
                
                print("\nTest Results:")
                print("-" * 20)
                print(result)
                print("=" * 50)
                
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                print(f"\nError with query '{query}': {str(e)}")
                continue
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        print(f"\nFatal error: {str(e)}")

if __name__ == "__main__":
    main() 