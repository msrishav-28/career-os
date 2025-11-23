from crewai import Crew, Task
from agents import create_profile_agent, create_outreach_agent
from typing import Dict


class OutreachCrew:
    """Crew that coordinates profile analysis and outreach message generation"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.profile_agent = create_profile_agent(user_id)
        self.outreach_agent = create_outreach_agent()
    
    def generate_outreach(self, contact: Dict, context: str) -> Dict:
        """Generate personalized outreach message for a contact"""
        
        # Task 1: Analyze user profile for relevant content
        profile_task = Task(
            description=f"""
            Query the user's profile to find the most relevant projects, skills, and experiences
            for reaching out to {contact.get('name')} at {contact.get('company')}.
            
            Context: {context}
            Contact's role: {contact.get('title')}
            
            Return the 2-3 most relevant items that would resonate with this contact.
            """,
            agent=self.profile_agent,
            expected_output="List of relevant user background items with explanations"
        )
        
        # Task 2: Generate personalized message
        outreach_task = Task(
            description=f"""
            Generate 3 personalized outreach message drafts for:
            
            Contact: {contact.get('name')}
            Title: {contact.get('title')}
            Company: {contact.get('company')}
            Context: {context}
            
            Use the profile analysis to craft authentic, personalized messages.
            Each draft should score 70+ on personalization.
            
            Include:
            1. Technical depth version
            2. Story-based version  
            3. Connection-first version
            
            Return JSON with all drafts and scores.
            """,
            agent=self.outreach_agent,
            expected_output="JSON with 3 message drafts, scores, and recommendations",
            context=[profile_task]
        )
        
        # Create and run crew
        crew = Crew(
            agents=[self.profile_agent, self.outreach_agent],
            tasks=[profile_task, outreach_task],
            verbose=True
        )
        
        result = crew.kickoff()
        return result
