from crewai import Agent
from config.prompts import (
    CRM_AGENT_ROLE,
    CRM_AGENT_GOAL,
    CRM_AGENT_BACKSTORY
)
from langchain_openai import ChatOpenAI
from config.settings import settings
from datetime import datetime, timedelta


def create_crm_agent() -> Agent:
    """
    Create the CRM Management Agent
    
    This agent tracks all contacts, manages follow-ups, and ensures no
    opportunity falls through the cracks.
    """
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.4,
        api_key=settings.OPENAI_API_KEY
    )
    
    agent = Agent(
        role=CRM_AGENT_ROLE,
        goal=CRM_AGENT_GOAL,
        backstory=CRM_AGENT_BACKSTORY,
        tools=[],  # CRM agent primarily uses database operations
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )
    
    return agent


def create_followup_analysis_prompt(messages: list, contact: dict) -> str:
    """Generate prompt for follow-up analysis"""
    
    prompt = f"""
Analyze the conversation history and determine follow-up strategy.

**Contact Information:**
Name: {contact.get('name')}
Company: {contact.get('company')}
Status: {contact.get('status')}
Quality Score: {contact.get('quality_score')}/10

**Message History:**
"""
    for msg in messages:
        prompt += f"\n- {msg.get('sent_at')}: Sent via {msg.get('platform')}"
        prompt += f"\n  Status: {msg.get('status')}"
        if msg.get('reply_content'):
            prompt += f"\n  Reply: {msg.get('reply_content')[:100]}..."
    
    prompt += f"""

**Your Task:**
1. Assess if follow-up is appropriate
   - Check for rejection signals ("not interested", "busy", etc.)
   - Consider time since last contact
   - Evaluate response likelihood

2. If follow-up recommended, suggest strategy:
   - New angle or information to share
   - Different value proposition
   - Optimal timing

3. If follow-up not recommended, explain why

**Decision Criteria:**
- Don't follow up if clear rejection
- Wait at least 7 days between contacts
- Maximum 2 follow-ups per campaign
- Respect their time and preferences

**Output Format (JSON):**
{{
    "should_followup": true/false,
    "reasoning": "explanation",
    "new_angle": "what new information to share",
    "timing": "when to send (e.g., '7 days from now')",
    "message_suggestion": "brief follow-up message"
}}
"""
    return prompt


def analyze_response_sentiment(reply_content: str) -> dict:
    """
    Analyze sentiment of a reply
    Returns: dict with sentiment and signals
    """
    reply_lower = reply_content.lower()
    
    # Positive signals
    positive_signals = [
        'yes', 'sure', 'sounds good', 'interested', 'love to',
        'happy to', 'would be great', 'schedule', 'call', 'meeting'
    ]
    
    # Negative signals
    negative_signals = [
        'not interested', 'no thank', 'not at this time', 'busy',
        'can\'t help', 'not the right', 'pass', 'decline'
    ]
    
    # Neutral signals
    neutral_signals = [
        'will review', 'get back to you', 'let me think',
        'keep in touch', 'maybe later', 'circle back'
    ]
    
    positive_count = sum(1 for signal in positive_signals if signal in reply_lower)
    negative_count = sum(1 for signal in negative_signals if signal in reply_lower)
    neutral_count = sum(1 for signal in neutral_signals if signal in reply_lower)
    
    if positive_count > negative_count and positive_count > 0:
        sentiment = 'positive'
        priority = 'high'
    elif negative_count > 0:
        sentiment = 'negative'
        priority = 'low'
    else:
        sentiment = 'neutral'
        priority = 'medium'
    
    return {
        'sentiment': sentiment,
        'priority': priority,
        'positive_signals': positive_count,
        'negative_signals': negative_count,
        'neutral_signals': neutral_count,
        'requires_action': sentiment == 'positive'
    }


def calculate_contact_priority(contact: dict, messages: list) -> int:
    """
    Calculate priority score for a contact (1-10)
    Higher score = higher priority
    """
    score = contact.get('quality_score', 5)
    
    # Boost for responses
    has_responded = any(msg.get('status') == 'replied' for msg in messages)
    if has_responded:
        score += 2
    
    # Boost for positive sentiment
    recent_replies = [msg for msg in messages if msg.get('reply_content')]
    if recent_replies:
        latest_reply = recent_replies[-1]
        sentiment_analysis = analyze_response_sentiment(latest_reply.get('reply_content', ''))
        if sentiment_analysis['sentiment'] == 'positive':
            score += 3
        elif sentiment_analysis['sentiment'] == 'negative':
            score -= 2
    
    # Boost for hiring managers
    if contact.get('title') and 'manager' in contact.get('title', '').lower():
        score += 1
    
    # Boost for dream companies
    dream_companies = ['google', 'meta', 'microsoft', 'openai', 'anthropic']
    if contact.get('company') and any(company in contact.get('company', '').lower() for company in dream_companies):
        score += 1
    
    # Reduce for old contacts with no response
    if messages and not has_responded:
        days_since_first = (datetime.now() - datetime.fromisoformat(messages[0].get('sent_at', datetime.now().isoformat()))).days
        if days_since_first > 14:
            score -= 1
    
    return min(max(score, 1), 10)  # Clamp between 1-10


def get_recommended_followup_timing(messages: list) -> str:
    """
    Get recommended timing for next follow-up
    """
    if not messages:
        return "immediate"
    
    last_message = messages[-1]
    last_sent = datetime.fromisoformat(last_message.get('sent_at', datetime.now().isoformat()))
    days_since = (datetime.now() - last_sent).days
    
    if days_since < 7:
        days_to_wait = 7 - days_since
        return f"{days_to_wait} days from now"
    elif days_since < 14:
        return "send follow-up now"
    else:
        return "final follow-up (last attempt)"
