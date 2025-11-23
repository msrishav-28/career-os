from crewai import Agent
from tools.linkedin_tools import LinkedInJobSearchTool, LinkedInProfileScraperTool
from tools.github_tools import (
    GitHubRepoSearchTool,
    GitHubContributorsTool,
    GitHubTrendingReposTool
)
from config.prompts import (
    DISCOVERY_AGENT_ROLE,
    DISCOVERY_AGENT_GOAL,
    DISCOVERY_AGENT_BACKSTORY
)
from langchain_openai import ChatOpenAI
from config.settings import settings


def create_discovery_agent() -> Agent:
    """
    Create the Opportunity Discovery Agent
    
    This agent finds and filters high-quality job opportunities, internships,
    and valuable professional connections that align with user's profile and goals.
    """
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.5,  # Moderate temperature for creative searching
        api_key=settings.OPENAI_API_KEY
    )
    
    tools = [
        LinkedInJobSearchTool(),
        LinkedInProfileScraperTool(),
        GitHubRepoSearchTool(),
        GitHubContributorsTool(),
        GitHubTrendingReposTool()
    ]
    
    agent = Agent(
        role=DISCOVERY_AGENT_ROLE,
        goal=DISCOVERY_AGENT_GOAL,
        backstory=DISCOVERY_AGENT_BACKSTORY,
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=8  # Allow more iterations for comprehensive searching
    )
    
    return agent


def create_job_discovery_prompt(user_goals: dict, skills: list) -> str:
    """Generate a prompt for job discovery"""
    
    prompt = f"""
Find relevant job opportunities and professional connections for the user.

**User Profile:**
Primary Goal: {user_goals.get('primary_goal', 'Career advancement')}
Target Role: {user_goals.get('target_role', 'AI/ML Engineer')}
Skills: {', '.join(skills[:10])}
Location Preference: {user_goals.get('location', 'India/Remote')}
Timeline: {user_goals.get('timeline', 'Next 3 months')}

**Your Tasks:**
1. Search LinkedIn for jobs matching the target role and skills
2. For each high-potential opportunity (match score >7):
   - Extract company and role details
   - Identify hiring manager if possible
   - Note application deadline
3. Search GitHub for relevant projects/communities
4. Identify 5-10 people to potentially connect with (contributors, hiring managers)

**Evaluation Criteria:**
- Skills match (how many required skills user has)
- Location fit (prioritize India/Remote)
- Company relevance (aligned with user interests)
- Seniority level (appropriate for user's experience)

**Output:**
List of opportunities with:
- Title, Company, URL
- Match Score (1-10)
- Required skills
- Hiring manager (if found)
- Why it's a good fit
"""
    return prompt


def create_network_discovery_prompt(interests: list, companies: list) -> str:
    """Generate a prompt for network discovery"""
    
    prompt = f"""
Discover high-value professional connections for the user.

**Target Profile:**
Interests: {', '.join(interests)}
Target Companies: {', '.join(companies)}

**Your Tasks:**
1. Find GitHub contributors in relevant open-source projects
2. Identify people working at target companies
3. Search for researchers/practitioners in user's interest areas

**For each contact, gather:**
- Name and current role
- Company
- LinkedIn/GitHub profile
- Recent work or posts
- Why they're a valuable connection
- Estimated quality score (1-10)

**Prioritize:**
- Hiring managers and team leads (career contacts)
- Alumni from user's institution
- Active contributors in user's tech stack
- People recently posting about hiring

**Output:**
List of 10-20 high-quality contacts with full details.
"""
    return prompt
