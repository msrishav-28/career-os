from crewai import Agent
from tools.chromadb_tools import ProfileQueryTool, StoreProfileTool
from config.prompts import (
    PROFILE_AGENT_ROLE,
    PROFILE_AGENT_GOAL,
    PROFILE_AGENT_BACKSTORY
)
from langchain_openai import ChatOpenAI
from config.settings import settings


def create_profile_agent(user_id: str = None) -> Agent:
    """
    Create the Profile Intelligence Agent
    
    This agent maintains accurate, up-to-date representation of user's skills,
    projects, experiences, and career goals. It uses RAG to answer questions
    about the user's qualifications.
    """
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.3,  # Lower temperature for factual responses
        api_key=settings.OPENAI_API_KEY
    )
    
    tools = [
        ProfileQueryTool(),
        StoreProfileTool()
    ]
    
    agent = Agent(
        role=PROFILE_AGENT_ROLE,
        goal=PROFILE_AGENT_GOAL,
        backstory=PROFILE_AGENT_BACKSTORY,
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )
    
    return agent


def create_profile_analysis_prompt(opportunity: dict, user_id: str) -> str:
    """Generate a prompt for profile analysis against an opportunity"""
    
    prompt = f"""
Analyze the user's profile for fit with this opportunity:

**Opportunity Details:**
Title: {opportunity.get('title', 'N/A')}
Company: {opportunity.get('company', 'N/A')}
Type: {opportunity.get('opportunity_type', 'N/A')}
Requirements: {', '.join(opportunity.get('requirements', []))}
Description: {opportunity.get('description', 'N/A')}

**Your Task:**
1. Query the user's profile for relevant skills, projects, and experiences
2. Calculate a match score (1-10) based on:
   - Skills alignment with requirements (40%)
   - Relevant project experience (30%)
   - Past experiences in similar roles (20%)
   - Goal alignment (10%)
3. Identify the user's 3 most relevant projects/experiences
4. List any skill gaps

**Output Format (JSON):**
{{
    "match_score": <1-10>,
    "relevant_skills": ["skill1", "skill2", ...],
    "relevant_projects": [
        {{"name": "project name", "relevance": "why it's relevant"}}
    ],
    "relevant_experiences": ["experience1", "experience2"],
    "skill_gaps": ["gap1", "gap2"],
    "reasoning": "explanation of the match score"
}}

User ID: {user_id}
"""
    return prompt
