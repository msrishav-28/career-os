from crewai import Agent
from tools.linkedin_tools import LinkedInJobSearchTool, LinkedInProfileScraperTool
from tools.github_tools import (
    GitHubRepoSearchTool,
    GitHubContributorsTool,
    GitHubTrendingReposTool
)
from tools.academic_tools import (
    GoogleScholarTool,
    ArXivSearchTool,
    UniversityFacultyScraperTool,
    ResearchMatchScoringTool
)
from config.prompts import (
    DISCOVERY_AGENT_ROLE,
    DISCOVERY_AGENT_GOAL,
    DISCOVERY_AGENT_BACKSTORY,
    RESEARCH_DISCOVERY_PROMPT
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


def create_research_discovery_agent() -> Agent:
    """
    Create specialized Research Discovery Agent for finding researchers
    
    This agent specifically finds researchers, professors, and labs for
    research internship opportunities.
    """
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4,  # Lower temperature for more focused research discovery
        api_key=settings.OPENAI_API_KEY
    )
    
    tools = [
        GoogleScholarTool(),
        ArXivSearchTool(),
        UniversityFacultyScraperTool(),
        ResearchMatchScoringTool(),
        LinkedInProfileScraperTool(),  # For additional context
    ]
    
    agent = Agent(
        role="Academic Research Scout and Researcher Matcher",
        goal="""Find high-quality researchers and labs that match the user's research 
        interests and are potentially open to research interns.""",
        backstory="""You are an expert academic scout who understands research landscapes. 
        You know how to identify active researchers, evaluate lab quality, and assess 
        mentor-mentee fit. You're skilled at finding researchers who are both excellent 
        scientists and good mentors for interns.""",
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=10  # More iterations for thorough research discovery
    )
    
    return agent


def create_researcher_discovery_prompt(
    research_interests: list,
    target_universities: list = None,
    user_background: dict = None
) -> str:
    """Generate a prompt for researcher discovery"""
    
    universities_str = ', '.join(target_universities) if target_universities else 'any top research institutions'
    
    prompt = f"""
{RESEARCH_DISCOVERY_PROMPT}

**User Profile:**
Research Interests: {', '.join(research_interests)}
Target Universities: {universities_str}
Background: {user_background.get('level', 'Undergraduate/Graduate student')}
Relevant Experience: {user_background.get('experience', 'N/A')}

**Your Tasks:**
1. Search for researchers in these areas: {', '.join(research_interests)}
2. For each potential researcher:
   - Use Google Scholar to find their recent publications
   - Check if they're actively publishing (last 2 years)
   - Verify their affiliation matches target institutions (if specified)
   - Use arXiv to find recent preprints (if in CS/Physics)
   - Try to find their lab website/faculty page
   - Calculate match score using ResearchMatchScoringTool

3. Prioritize researchers who:
   - Have 1-3 recent publications in target area
   - Are at target institutions (if specified)
   - Have clear lab websites (shows they're organized)
   - Work on problems aligned with user interests
   - Have reasonable citation counts (active but not too senior to mentor)

4. For EACH researcher in your final list:
   - Fetch top 3 recent papers (title, year, key contribution)
   - Extract research keywords/interests
   - Find contact email and lab URL
   - Calculate and explain match score (1-10)
   - Suggest personalization angle for outreach

**Output Format:**
Return 20-30 high-quality researcher matches ranked by match score (highest first).

For each researcher provide:
```
Name: [Full Name]
Affiliation: [University/Institution]
Email: [Contact email]
Lab URL: [Lab website]
Research Areas: [List of interests]
Recent Publications:
  1. [Title] (Year) - [Key contribution]
  2. [Title] (Year) - [Key contribution]
  3. [Title] (Year) - [Key contribution]
Match Score: [X/10]
Match Reasoning: [Why this is a good match]
Recommended Angle: [How to approach this researcher]
```

Focus on QUALITY over quantity. Every researcher should be a genuine good fit.
"""
    return prompt
