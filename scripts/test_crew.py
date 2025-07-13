import asyncio
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY not found in environment variables!")

class SimpleTestCrew:
    def __init__(self):
        # Initialize with GPT-4
        self.llm = LLM(model="gpt-4o-mini", temperature=0)
        
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
        return f"Found information about: {query}"
        
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
        return f"Analysis of: {data}"
        
    def run_test_task(self, query: str):
        # Create tasks
        tasks = [
            Task(
                description=f"Research this topic: {query}",
                agent=self.researcher,
                expected_output="Detailed information about the requested topic"
            ),
            Task(
                description=f"Analyze the research findings about: {query}",
                agent=self.analyst,
                expected_output="Analysis and insights from the research findings"
            )
        ]
        
        # Create crew
        crew = Crew(
            agents=[self.researcher, self.analyst],
            tasks=tasks,
            verbose=True
        )
        
        # Run the crew
        result = crew.kickoff()
        return result

def main():
    # Create test crew
    test_crew = SimpleTestCrew()
    
    # Test query
    query = "Tell me about artificial intelligence"
    
    try:
        print("\nStarting CrewAI test...")
        result = test_crew.run_test_task(query)
        print("\nTest Results:")
        print(result)
        
    except Exception as e:
        print(f"\nError during test: {str(e)}")

if __name__ == "__main__":
    main() 