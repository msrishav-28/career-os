"""
Research Discovery Agent.

Per RESEARCH_MODULE.md §Agents:
  - Specialized agent for executing academic search strategies
  - Uses GoogleScholarTool, ArXivSearchTool, UniversityFacultyScraperTool
  - Works with the research-specific prompts in config/prompts.py
"""
from crewai import Agent
from config.prompts import (
    RESEARCH_DISCOVERY_PROMPT,
    RESEARCH_OUTREACH_CRITERIA,
    RESEARCH_MATCH_CRITERIA,
)
from langchain_openai import ChatOpenAI
from config.settings import settings
from typing import List


def create_research_agent() -> Agent:
    """
    Create the Research Discovery Agent.

    This agent specializes in finding academic researchers, professors,
    and research labs that match the user's interests for research
    internship campaigns.

    From RESEARCH_MODULE.md:
    - Google Scholar integration for researcher profiles
    - arXiv search for recent papers
    - Faculty page scraping
    - Match scoring based on publication relevance
    """

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY,
    )

    # Import tools (they may fail gracefully if scholarly/arxiv not installed)
    tools = []
    try:
        from tools.academic_tools import (
            GoogleScholarTool,
            ArXivSearchTool,
        )
        tools.append(GoogleScholarTool())
        tools.append(ArXivSearchTool())
    except ImportError:
        pass

    agent = Agent(
        role="Research Internship Scout",
        goal=(
            "Find and evaluate academic researchers for research internship "
            "opportunities. Identify professors with active labs, recent "
            "publications, and research alignment with the user's interests."
        ),
        backstory=(
            "You are a seasoned academic networker who understands the research "
            "landscape deeply. You know how to find the right professors, evaluate "
            "lab cultures from publications, and assess research fit. You prioritize "
            "researchers with recent, high-impact publications in the user's areas "
            "of interest. You understand that research internships require genuine "
            "technical alignment, not just superficial interest."
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10,
    )

    return agent


def create_research_outreach_agent() -> Agent:
    """
    Create the Research Outreach Agent.

    Generates academic-quality outreach emails that meet the 80/100
    quality bar per RESEARCH_MODULE.md and RESEARCH_OUTREACH_CRITERIA.
    """

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,
        api_key=settings.OPENAI_API_KEY,
    )

    agent = Agent(
        role="Academic Outreach Specialist",
        goal=(
            "Generate highly personalized academic outreach emails that "
            "reference specific publications, demonstrate technical depth, "
            "and meet the 80/100 quality threshold for research internship "
            "communications."
        ),
        backstory=(
            "You are an expert at crafting academic outreach emails. You know "
            "that professors receive dozens of generic emails daily, so you "
            "focus on specific technical details from their recent publications. "
            "You write concise (150-200 word) emails that demonstrate genuine "
            "understanding of the research and clear technical credibility.\n\n"
            f"Quality criteria:\n{RESEARCH_OUTREACH_CRITERIA}"
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )

    return agent
