from crewai import Crew, Task
from agents import create_profile_agent, create_discovery_agent
from typing import Dict, List


class DiscoveryCrew:
    """Crew that coordinates profile matching and opportunity discovery"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile_agent = create_profile_agent(user_id)
        self.discovery_agent = create_discovery_agent()
    
    def discover_opportunities(self, search_params: Dict) -> List[Dict]:
        """Discover and match opportunities to user profile"""
        
        # Task 1: Extract user goals and preferences
        profile_task = Task(
            description=f"""
            Extract from the user profile:
            - Career goals and target roles
            - Top 10 technical skills
            - Location preferences
            - Company/industry interests
            
            User ID: {self.user_id}
            """,
            agent=self.profile_agent,
            expected_output="Structured summary of user goals and preferences"
        )
        
        # Task 2: Search for opportunities
        discovery_task = Task(
            description=f"""
            Search for opportunities matching these criteria:
            
            Keywords: {search_params.get('keywords', 'AI ML internship')}
            Location: {search_params.get('location', 'India')}
            Type: {search_params.get('type', 'internship')}
            
            Use the user's profile to:
            1. Search LinkedIn jobs
            2. Find relevant GitHub projects/contributors
            3. Identify hiring managers and key contacts
            
            For each opportunity, calculate match score (1-10) based on:
            - Skills alignment
            - Location fit
            - Company relevance
            - Role seniority match
            
            Return top 10 opportunities with full details.
            """,
            agent=self.discovery_agent,
            expected_output="List of opportunities with match scores and contact info",
            context=[profile_task]
        )
        
        crew = Crew(
            agents=[self.profile_agent, self.discovery_agent],
            tasks=[profile_task, discovery_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return result
