from crewai import Agent
from config.prompts import CONTENT_AGENT_ROLE, CONTENT_AGENT_GOAL, CONTENT_AGENT_BACKSTORY
from langchain_openai import ChatOpenAI
from config.settings import settings
from typing import List, Dict
import re


def create_content_agent() -> Agent:
    """Create the Content Curation Agent"""
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.6,
        api_key=settings.OPENAI_API_KEY
    )
    
    agent = Agent(
        role=CONTENT_AGENT_ROLE,
        goal=CONTENT_AGENT_GOAL,
        backstory=CONTENT_AGENT_BACKSTORY,
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )
    
    return agent


def score_content_quality(content: Dict) -> int:
    """
    Score content quality (1-10)
    """
    score = 5  # Base score
    
    text = content.get('text', '').lower()
    author = content.get('author', {})
    
    # Technical depth indicators (+3)
    technical_keywords = ['research', 'paper', 'algorithm', 'model', 'architecture', 'implementation', 'code', 'dataset']
    tech_count = sum(1 for keyword in technical_keywords if keyword in text)
    if tech_count >= 3:
        score += 3
    elif tech_count >= 1:
        score += 1
    
    # Avoid generic motivational content (-2)
    generic_keywords = ['motivation', 'inspire', 'hustle', 'grind', 'mindset', 'success secrets']
    if any(keyword in text for keyword in generic_keywords):
        score -= 2
    
    # Author credibility (+2)
    if author.get('followers', 0) > 10000:
        score += 1
    if author.get('verified', False):
        score += 1
    
    # Engagement quality (+1)
    if content.get('likes', 0) > 100:
        score += 1
    
    # Length appropriateness (+1)
    word_count = len(text.split())
    if 50 <= word_count <= 500:  # Good length
        score += 1
    
    return min(max(score, 1), 10)


def identify_engagement_opportunities(posts: List[Dict], user_profile: Dict) -> List[Dict]:
    """
    Identify posts worth engaging with
    """
    opportunities = []
    
    for post in posts:
        opp_score = 0
        reasons = []
        
        text = post.get('text', '').lower()
        author = post.get('author', {})
        
        # Question asked (+3)
        if '?' in text:
            opp_score += 3
            reasons.append("Author asked a question")
        
        # Related to user's expertise (+4)
        user_skills = [skill.lower() for skill in user_profile.get('skills', [])]
        skill_mentions = sum(1 for skill in user_skills if skill in text)
        if skill_mentions > 0:
            opp_score += 4
            reasons.append(f"Mentions your expertise: {skill_mentions} skills")
        
        # From target company (+3)
        target_companies = user_profile.get('target_companies', [])
        if any(company.lower() in author.get('company', '').lower() for company in target_companies):
            opp_score += 3
            reasons.append("Author works at target company")
        
        # Alumni connection (+2)
        if user_profile.get('alma_mater', '').lower() in author.get('bio', '').lower():
            opp_score += 2
            reasons.append("Alumni connection")
        
        # Recent post (+1)
        hours_old = post.get('hours_old', 999)
        if hours_old < 6:
            opp_score += 1
            reasons.append("Recent post (high visibility)")
        
        if opp_score >= 5:  # Threshold
            opportunities.append({
                'post': post,
                'opportunity_score': opp_score,
                'reasons': reasons,
                'suggested_response_type': _suggest_response_type(post, user_profile)
            })
    
    # Sort by score
    opportunities.sort(key=lambda x: x['opportunity_score'], reverse=True)
    
    return opportunities[:10]  # Top 10


def _suggest_response_type(post: Dict, user_profile: Dict) -> str:
    """Suggest what type of response to make"""
    text = post.get('text', '').lower()
    
    if '?' in text:
        return "answer_question"
    elif 'experience' in text or 'thoughts' in text:
        return "share_experience"
    elif 'announce' in text or 'launch' in text:
        return "congratulate"
    elif 'challenge' in text or 'problem' in text:
        return "offer_solution"
    else:
        return "insightful_comment"


def generate_comment_draft(post: Dict, response_type: str, user_profile: Dict) -> str:
    """Generate a draft comment"""
    
    templates = {
        'answer_question': "Great question! Based on my experience with {skill}, {insight}. Have you considered {suggestion}?",
        'share_experience': "This resonates with my work on {project}. I found that {insight}. Would love to discuss further!",
        'congratulate': "Congratulations! This is exciting. Your work on {topic} is really pushing boundaries. Looking forward to seeing the impact.",
        'offer_solution': "Interesting challenge. I tackled something similar in {project}. {solution_approach}. Happy to share more details if helpful.",
        'insightful_comment': "Excellent point about {topic}. This aligns with what I've seen in {context}. {additional_insight}."
    }
    
    template = templates.get(response_type, templates['insightful_comment'])
    
    # This is a simplified version - in production, use LLM to generate fully personalized
    return template


def analyze_feed_health(posts: List[Dict]) -> Dict:
    """Analyze feed quality and suggest improvements"""
    
    total_posts = len(posts)
    if total_posts == 0:
        return {"status": "no_data"}
    
    # Categorize content
    categories = {
        'technical': 0,
        'motivational': 0,
        'promotional': 0,
        'news': 0,
        'personal': 0
    }
    
    for post in posts:
        text = post.get('text', '').lower()
        
        if any(word in text for word in ['research', 'code', 'algorithm', 'implementation']):
            categories['technical'] += 1
        if any(word in text for word in ['inspire', 'motivation', 'mindset']):
            categories['motivational'] += 1
        if any(word in text for word in ['buy', 'sale', 'discount', 'link in bio']):
            categories['promotional'] += 1
        if any(word in text for word in ['breaking', 'news', 'announced']):
            categories['news'] += 1
        if any(word in text for word in ['grateful', 'journey', 'personal']):
            categories['personal'] += 1
    
    # Calculate percentages
    percentages = {k: round(v / total_posts * 100, 1) for k, v in categories.items()}
    
    # Generate recommendations
    recommendations = []
    
    if percentages['technical'] < 30:
        recommendations.append("Follow more technical experts in your field")
    if percentages['motivational'] > 40:
        recommendations.append("Reduce motivational content, focus on actionable insights")
    if percentages['promotional'] > 20:
        recommendations.append("Mute accounts that are overly promotional")
    
    return {
        'total_analyzed': total_posts,
        'content_breakdown': percentages,
        'recommendations': recommendations,
        'feed_quality_score': calculate_feed_quality_score(percentages)
    }


def calculate_feed_quality_score(percentages: Dict) -> int:
    """Calculate overall feed quality (1-10)"""
    score = 5
    
    # Reward technical content
    if percentages['technical'] > 40:
        score += 3
    elif percentages['technical'] > 20:
        score += 1
    
    # Penalize excessive motivational
    if percentages['motivational'] > 50:
        score -= 3
    elif percentages['motivational'] > 30:
        score -= 1
    
    # Penalize promotional spam
    if percentages['promotional'] > 30:
        score -= 2
    
    return min(max(score, 1), 10)


def create_daily_digest(curated_posts: List[Dict], opportunities: List[Dict]) -> Dict:
    """Create daily digest email content"""
    
    digest = {
        'date': '2024-01-01',  # Use actual date
        'top_posts': curated_posts[:5],
        'engagement_opportunities': opportunities[:3],
        'summary': f"Today's digest: {len(curated_posts)} high-quality posts, {len(opportunities)} engagement opportunities"
    }
    
    return digest
