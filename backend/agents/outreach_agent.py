from crewai import Agent
from tools.chromadb_tools import ProfileQueryTool, TemplateQueryTool
from tools.email_tools import EmailTemplateTool
from config.prompts import (
    OUTREACH_AGENT_ROLE,
    OUTREACH_AGENT_GOAL,
    OUTREACH_AGENT_BACKSTORY,
    OUTREACH_QUALITY_CRITERIA,
    RESEARCH_OUTREACH_CRITERIA,
    RESEARCH_EMAIL_TEMPLATE
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


def create_research_outreach_prompt(researcher: dict, user_profile: dict, campaign_context: dict) -> str:
    """
    Generate a prompt for research internship outreach message creation
    
    Args:
        researcher: Dict with researcher details (publications, interests, etc.)
        user_profile: Dict with user's research background
        campaign_context: Dict with campaign details (timeline, specific goals)
    
    Returns:
        Prompt for generating research outreach email
    """
    
    # Extract researcher's most recent publication
    publications = researcher.get('publications', [])
    recent_pub = publications[0] if publications else {'title': 'N/A', 'year': 'N/A'}
    
    prompt = f"""
Generate a research internship inquiry email for this researcher.

**Researcher Profile:**
Name: {researcher.get('name')}
Affiliation: {researcher.get('company', researcher.get('affiliation', 'N/A'))}
Research Areas: {', '.join(researcher.get('research_areas', []))}
Recent Publications:
"""
    
    # Add up to 3 recent publications
    for i, pub in enumerate(publications[:3], 1):
        prompt += f"  {i}. {pub.get('title', 'N/A')} ({pub.get('year', 'N/A')})\n"
    
    prompt += f"""
Lab URL: {researcher.get('lab_url', 'N/A')}
Match Score: {researcher.get('quality_score', 'N/A')}/10

**Your Profile:**
Name: {user_profile.get('name')}
Affiliation: {user_profile.get('affiliation', user_profile.get('university', 'N/A'))}
Research Interests: {', '.join(user_profile.get('research_interests', []))}
Relevant Projects: {', '.join(user_profile.get('projects', [])[:2])}
Technical Background: {user_profile.get('technical_skills', 'N/A')}

**Campaign Context:**
Timeline: {campaign_context.get('timeline', 'Summer 2025')}
Duration: {campaign_context.get('duration', '10-12 weeks')}
Goals: {campaign_context.get('goals', 'Gain research experience')}

**Quality Criteria:**
{RESEARCH_OUTREACH_CRITERIA}

**Your Task:**
Generate a highly personalized research internship inquiry email.

**CRITICAL REQUIREMENTS**:
1. Reference their MOST RECENT publication by exact title
2. Mention a SPECIFIC technical detail from their work (methodology, finding, approach)
3. Connect to YOUR most relevant project with CONCRETE details (not generic)
4. Show technical depth - use proper terminology from their field
5. Keep it 150-200 words (professors are busy)
6. Ask respectfully about research opportunities (don't demand internship)
7. Mention timeline (e.g., "Summer 2025")
8. Offer to share CV/research statement

**Output Format (JSON)**:
{{
    "subject": "Research Internship Inquiry - [Specific Area]",
    "email_body": "...",
    "personalization_score": 85,
    "reasoning": "Detailed explanation of personalization elements",
    "technical_depth_score": 8,
    "research_fit_score": 9
}}

**Template Structure to Follow**:
{RESEARCH_EMAIL_TEMPLATE}

Generate an email that would make the researcher think:
"This student has actually read my work and knows what they're talking about."

Minimum acceptable score: 80/100 (research emails require higher quality than industry)
"""
    
    return prompt


def calculate_research_personalization_score(message: str, researcher: dict, user_info: dict) -> dict:
    """
    Calculate personalization score specifically for research outreach emails
    
    Args:
        message: The email message
        researcher: Researcher profile dict
        user_info: User profile dict
    
    Returns:
        Dict with score breakdown and recommendations
    """
    score = 0
    breakdown = {}
    
    # 1. Academic Specificity (30 points)
    publications = researcher.get('publications', [])
    if publications:
        # Check if specific paper title is mentioned
        paper_mentioned = any(
            pub.get('title', '').lower()[:30] in message.lower()
            for pub in publications[:3]
        )
        if paper_mentioned:
            score += 20
            breakdown['mentions_specific_paper'] = 20
            
            # Check for technical detail (not just paper title)
            technical_terms = ['method', 'approach', 'algorithm', 'framework', 'model', 
                             'technique', 'finding', 'result', 'dataset']
            if any(term in message.lower() for term in technical_terms):
                score += 10
                breakdown['mentions_technical_detail'] = 10
        else:
            # At least mentions research area
            research_areas = researcher.get('research_areas', [])
            if any(area.lower() in message.lower() for area in research_areas):
                score += 10
                breakdown['mentions_research_area'] = 10
    
    # 2. Technical Credibility (25 points)
    user_projects = user_info.get('projects', [])
    if user_projects and any(proj.lower() in message.lower() for proj in user_projects[:2]):
        score += 15
        breakdown['mentions_user_project'] = 15
        
        # Check for quantitative results (shows serious work)
        if any(char.isdigit() and '%' in message[i:i+10] 
               for i, char in enumerate(message) if char.isdigit()):
            score += 10
            breakdown['includes_quantitative_results'] = 10
    
    # 3. Clear Research Fit (20 points)
    research_interests = researcher.get('research_areas', [])
    user_interests = user_info.get('research_interests', [])
    
    # Check for overlap in interests mentioned
    overlap_count = sum(
        1 for interest in user_interests 
        if any(area.lower() in interest.lower() or interest.lower() in area.lower() 
               for area in research_interests)
    )
    
    if overlap_count >= 2:
        score += 20
        breakdown['strong_research_fit'] = 20
    elif overlap_count == 1:
        score += 10
        breakdown['moderate_research_fit'] = 10
    
    # 4. Appropriate Length (10 points)
    word_count = len(message.split())
    if 150 <= word_count <= 200:
        score += 10
        breakdown['optimal_length'] = 10
    elif 120 <= word_count < 150 or 200 < word_count <= 250:
        score += 5
        breakdown['acceptable_length'] = 5
    
    # 5. Respectful Ask (15 points)
    respectful_phrases = [
        'would you', 'could you', 'would love to', 'interested in discussing',
        'explore opportunities', 'available for', 'open to'
    ]
    if any(phrase in message.lower() for phrase in respectful_phrases):
        score += 10
        breakdown['respectful_inquiry'] = 10
        
    # Check for timeline mention
    timeline_keywords = ['summer', 'fall', 'spring', 'winter', '2024', '2025', '2026']
    if any(keyword in message.lower() for keyword in timeline_keywords):
        score += 5
        breakdown['mentions_timeline'] = 5
    
    # Calculate sub-scores
    technical_depth = breakdown.get('mentions_technical_detail', 0) + \
                     breakdown.get('includes_quantitative_results', 0)
    research_fit = breakdown.get('strong_research_fit', 0) + \
                   breakdown.get('moderate_research_fit', 0)
    
    return {
        'score': min(score, 100),
        'breakdown': breakdown,
        'passed': score >= 80,  # Higher threshold for research emails
        'technical_depth_score': min(technical_depth // 2, 10),
        'research_fit_score': min(research_fit // 2, 10),
        'recommendation': 'Excellent' if score >= 90 else 'Good' if score >= 80 else 'Needs improvement'
    }


def validate_research_email_quality(message: str, researcher: dict, min_score: int = 80) -> tuple[bool, str]:
    """
    Validate research email meets academic standards
    
    Args:
        message: Email message
        researcher: Researcher profile
        min_score: Minimum acceptable score (default 80 for research)
    
    Returns:
        (is_valid, error_message)
    """
    # Check basic quality first
    is_valid, error = validate_message_quality(message, min_score)
    if not is_valid:
        return is_valid, error
    
    # Additional checks for research emails
    publications = researcher.get('publications', [])
    
    # Must reference at least one publication or research area
    research_areas = researcher.get('research_areas', [])
    has_research_reference = any(
        pub.get('title', '').lower()[:20] in message.lower()
        for pub in publications[:3]
    ) or any(
        area.lower() in message.lower()
        for area in research_areas
    )
    
    if not has_research_reference:
        return False, "Research email must reference specific work or research area"
    
    # Check for generic phrases that indicate low effort
    generic_phrases = [
        'i read your papers',
        'your research is interesting',
        'i am interested in your lab',
        'do you have any internship',
        'i want to work with you'
    ]
    
    if any(phrase in message.lower() for phrase in generic_phrases):
        return False, f"Email contains generic phrases - be more specific about their research"
    
    # Check minimum length for research emails
    word_count = len(message.split())
    if word_count < 120:
        return False, "Research email too short - should be 150-200 words for substantive content"
    
    return True, "Research email passes quality checks"
