from crewai import Agent
from config.prompts import GROWTH_AGENT_ROLE, GROWTH_AGENT_GOAL, GROWTH_AGENT_BACKSTORY
from langchain_openai import ChatOpenAI
from config.settings import settings


def create_growth_agent() -> Agent:
    """Create the Growth Advisory Agent"""
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        api_key=settings.OPENAI_API_KEY
    )
    
    agent = Agent(
        role=GROWTH_AGENT_ROLE,
        goal=GROWTH_AGENT_GOAL,
        backstory=GROWTH_AGENT_BACKSTORY,
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )
    
    return agent
