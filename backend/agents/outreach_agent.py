from crewai import Agent
from tools.chromadb_tools import ProfileQueryTool, TemplateQueryTool
from tools.email_tools import EmailTemplateTool
from config.prompts import (
    OUTREACH_AGENT_ROLE,
    OUTREACH_AGENT_GOAL,
    OUTREACH_AGENT_BACKSTORY,
    OUTREACH_QUALITY_CRITERIA
)
from langchain_openai import ChatOpenAI
from config.settings import settings
import re


def create_outreach_agent() -> Agent:
    """
    Create the Outreach Automation Agent
    
    This agent generates personalized, high-quality outreach messages that
    start meaningful professional conversations.
    """
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,  # Higher temperature for creative, natural messages
        api_key=settings.OPENAI_API_KEY
    )
    
    tools = [
        ProfileQueryTool(),
        TemplateQueryTool(),
        EmailTemplateTool()
    ]
    
    agent = Agent(
        role=OUTREACH_AGENT_ROLE,
        goal=OUTREACH_AGENT_GOAL,
        backstory=OUTREACH_AGENT_BACKSTORY,
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=6
    )
    
    return agent


def create_outreach_prompt(contact: dict, user_profile: dict, context: str) -> str:
    """Generate a prompt for outreach message creation"""
    
    prompt = f"""
Generate a personalized outreach message for this contact.

**Contact Information:**
Name: {contact.get('name')}
Title: {contact.get('title', 'N/A')}
Company: {contact.get('company', 'N/A')}
Recent Activity: {contact.get('recent_activity', 'Not available')}
Why Reaching Out: {context}

**User Profile:**
Name: {user_profile.get('name')}
Background: {user_profile.get('background')}
Relevant Projects: {user_profile.get('relevant_projects', [])}
Shared Interests: {user_profile.get('shared_interests', [])}

**Quality Criteria:**
{OUTREACH_QUALITY_CRITERIA}

**Your Task:**
Generate 3 different message styles:

1. **Technical Depth Version**
   - Lead with specific technical work (theirs or yours)
   - Deep dive into shared technical interests
   - Professional and detailed

2. **Story-Based Version**
   - Open with compelling project narrative
   - Show your journey and passion
   - Warm and engaging

3. **Connection-First Version**
   - Emphasize common ground (alumni, interests, mutual connections)
   - Brief and respectful
   - Focus on relationship building

**For each version:**
- Calculate personalization score (0-100)
- Include subject line (for email) or opening (for LinkedIn)
- Keep appropriate length
- Explain scoring reasoning

**Critical Requirements:**
- Reference SPECIFIC recent work by the contact
- Mention user's MOST RELEVANT project
- Clear, respectful call-to-action
- Natural, human tone (not templated)
- No placeholders like [NAME] or {{variable}}

**Output Format (JSON):**
{{
    "drafts": [
        {{
            "style": "technical_depth",
            "platform": "email or linkedin",
            "subject": "...",
            "message": "...",
            "personalization_score": 75,
            "reasoning": "..."
        }},
        // ... 2 more drafts
    ],
    "recommended_draft": 0,
    "overall_recommendation": "Use technical depth version because..."
}}
"""
    return prompt


def calculate_personalization_score(message: str, contact: dict, user_info: dict) -> dict:
    """
    Calculate personalization score for a message
    Returns: dict with score and breakdown
    """
    score = 0
    breakdown = {}
    
    # Check for specific personalization elements (30 points)
    contact_name = contact.get('name', '').split()[0] if contact.get('name') else ''
    if contact_name and contact_name in message:
        score += 5
        breakdown['uses_name'] = 5
    
    # Check for reference to their work (30 points)
    recent_activity = contact.get('recent_activity', '').lower()
    company = contact.get('company', '').lower()
    
    if recent_activity and any(word in message.lower() for word in recent_activity.split()[:5]):
        score += 25
        breakdown['references_their_work'] = 25
    elif company and company in message.lower():
        score += 15
        breakdown['mentions_company'] = 15
    
    # Check for user's relevant background (20 points)
    user_projects = user_info.get('relevant_projects', [])
    if user_projects and any(proj.lower() in message.lower() for proj in user_projects):
        score += 20
        breakdown['mentions_user_project'] = 20
    
    # Check for clear call-to-action (15 points)
    cta_phrases = ['would you', 'could you', 'open to', 'available for', 'schedule', 'call', 'coffee']
    if any(phrase in message.lower() for phrase in cta_phrases):
        score += 15
        breakdown['has_clear_cta'] = 15
    
    # Check length appropriateness (10 points)
    word_count = len(message.split())
    if 100 <= word_count <= 250:  # Optimal length
        score += 10
        breakdown['appropriate_length'] = 10
    elif 50 <= word_count < 100 or 250 < word_count <= 350:
        score += 5
        breakdown['acceptable_length'] = 5
    
    # Check for natural tone (15 points)
    # Avoid over-use of "I" (self-focused)
    i_count = message.lower().count(' i ')
    if i_count <= 3:
        score += 8
        breakdown['balanced_perspective'] = 8
    
    # Check for no placeholders
    placeholders = re.findall(r'\[.*?\]|\{.*?\}', message)
    if not placeholders:
        score += 7
        breakdown['no_placeholders'] = 7
    
    # Mutual benefit (10 points)
    benefit_words = ['help', 'learn', 'share', 'discuss', 'explore', 'collaborate']
    if any(word in message.lower() for word in benefit_words):
        score += 10
        breakdown['shows_mutual_benefit'] = 10
    
    return {
        'score': min(score, 100),  # Cap at 100
        'breakdown': breakdown,
        'passed': score >= 70
    }


def validate_message_quality(message: str, min_score: int = 70) -> tuple[bool, str]:
    """
    Validate message meets quality standards
    Returns: (is_valid, error_message)
    """
    # Check for placeholders
    placeholders = re.findall(r'\[.*?\]|\{\{.*?\}\}', message)
    if placeholders:
        return False, f"Message contains unfilled placeholders: {placeholders}"
    
    # Check length
    word_count = len(message.split())
    if word_count < 30:
        return False, "Message too short (minimum 30 words)"
    if word_count > 400:
        return False, "Message too long (maximum 400 words)"
    
    # Check for excessive "I" usage
    i_count = message.lower().count(' i ')
    if i_count > 5:
        return False, "Message too self-focused (too many 'I' statements)"
    
    return True, "Message passes quality checks"
