from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from services import supabase_service
import asyncio


class AnalyticsEngine:
    """Analytics engine for CareerOS metrics and insights"""
    
    @staticmethod
    async def get_outreach_metrics(user_id: str, days: int = 30) -> Dict:
        """Get comprehensive outreach metrics"""
        
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get all messages in period
        messages = await supabase_service.get_messages(user_id, limit=10000)
        period_messages = [m for m in messages if m.get('created_at', '') >= cutoff_date]
        
        # Calculate metrics
        total_sent = len([m for m in period_messages if m.get('status') in ['sent', 'opened', 'replied']])
        total_opened = len([m for m in period_messages if m.get('status') in ['opened', 'replied']])
        total_replied = len([m for m in period_messages if m.get('status') == 'replied'])
        
        # Response rates
        open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
        response_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0
        
        # Platform breakdown
        by_platform = {}
        for platform in ['email', 'linkedin', 'twitter']:
            platform_msgs = [m for m in period_messages if m.get('platform') == platform]
            platform_sent = len([m for m in platform_msgs if m.get('status') in ['sent', 'opened', 'replied']])
            platform_replied = len([m for m in platform_msgs if m.get('status') == 'replied'])
            
            by_platform[platform] = {
                'sent': platform_sent,
                'replied': platform_replied,
                'response_rate': (platform_replied / platform_sent * 100) if platform_sent > 0 else 0
            }
        
        # Average personalization score
        avg_personalization = sum(m.get('personalization_score', 0) for m in period_messages) / len(period_messages) if period_messages else 0
        
        # Time series data (daily breakdown)
        daily_stats = AnalyticsEngine._calculate_daily_stats(period_messages, days)
        
        return {
            'period_days': days,
            'total_sent': total_sent,
            'total_opened': total_opened,
            'total_replied': total_replied,
            'open_rate': round(open_rate, 1),
            'response_rate': round(response_rate, 1),
            'avg_personalization_score': round(avg_personalization, 1),
            'by_platform': by_platform,
            'daily_stats': daily_stats
        }
    
    @staticmethod
    def _calculate_daily_stats(messages: List[Dict], days: int) -> List[Dict]:
        """Calculate daily stats for time series"""
        daily = {}
        
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            daily[date] = {'sent': 0, 'replied': 0, 'response_rate': 0}
        
        for msg in messages:
            date = msg.get('sent_at', '')[:10] if msg.get('sent_at') else ''
            if date in daily:
                if msg.get('status') in ['sent', 'opened', 'replied']:
                    daily[date]['sent'] += 1
                if msg.get('status') == 'replied':
                    daily[date]['replied'] += 1
        
        # Calculate response rates
        for date in daily:
            if daily[date]['sent'] > 0:
                daily[date]['response_rate'] = round(daily[date]['replied'] / daily[date]['sent'] * 100, 1)
        
        # Convert to list sorted by date
        return [{'date': date, **stats} for date, stats in sorted(daily.items())]
    
    @staticmethod
    async def get_pipeline_metrics(user_id: str) -> Dict:
        """Get CRM pipeline metrics"""
        
        contacts = await supabase_service.get_contacts(user_id, limit=10000)
        
        # Count by status
        by_status = {}
        status_values = ['discovered', 'to_contact', 'contacted', 'responded', 'in_conversation', 'converted', 'inactive']
        
        for status in status_values:
            by_status[status] = len([c for c in contacts if c.get('status') == status])
        
        # Conversion rates
        total_contacted = by_status.get('contacted', 0) + by_status.get('responded', 0) + by_status.get('in_conversation', 0) + by_status.get('converted', 0)
        total_responded = by_status.get('responded', 0) + by_status.get('in_conversation', 0) + by_status.get('converted', 0)
        total_converted = by_status.get('converted', 0)
        
        contact_to_response = (total_responded / total_contacted * 100) if total_contacted > 0 else 0
        response_to_conversion = (total_converted / total_responded * 100) if total_responded > 0 else 0
        
        # Average quality score
        avg_quality = sum(c.get('quality_score', 0) for c in contacts) / len(contacts) if contacts else 0
        
        # Top contacts
        top_contacts = sorted(contacts, key=lambda x: x.get('quality_score', 0), reverse=True)[:10]
        
        return {
            'total_contacts': len(contacts),
            'by_status': by_status,
            'conversion_rates': {
                'contact_to_response': round(contact_to_response, 1),
                'response_to_conversion': round(response_to_conversion, 1)
            },
            'avg_quality_score': round(avg_quality, 1),
            'top_contacts': top_contacts
        }
    
    @staticmethod
    async def get_campaign_performance(user_id: str) -> List[Dict]:
        """Get performance metrics for all campaigns"""
        
        campaigns = await supabase_service.get_campaigns(user_id)
        performance = []
        
        for campaign in campaigns:
            campaign_id = campaign['id']
            
            # Get campaign messages
            messages = await supabase_service.get_messages(user_id, campaign_id=campaign_id)
            
            total_sent = len([m for m in messages if m.get('status') in ['sent', 'opened', 'replied']])
            total_replied = len([m for m in messages if m.get('status') == 'replied'])
            
            response_rate = (total_replied / total_sent * 100) if total_sent > 0 else 0
            avg_personalization = sum(m.get('personalization_score', 0) for m in messages) / len(messages) if messages else 0
            
            performance.append({
                'campaign_id': campaign_id,
                'campaign_name': campaign['name'],
                'campaign_type': campaign['campaign_type'],
                'total_sent': total_sent,
                'total_replied': total_replied,
                'response_rate': round(response_rate, 1),
                'avg_personalization': round(avg_personalization, 1),
                'status': campaign['status']
            })
        
        return performance
    
    @staticmethod
    async def identify_skill_gaps(user_id: str) -> Dict:
        """Identify skill gaps based on viewed opportunities"""
        
        opportunities = await supabase_service.get_opportunities(user_id, limit=1000)
        
        # Extract all required skills
        all_requirements = []
        for opp in opportunities:
            all_requirements.extend(opp.get('requirements', []))
        
        # Count frequency
        skill_frequency = {}
        for skill in all_requirements:
            skill = skill.lower().strip()
            skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
        
        # Get user's current skills
        user_profile = chroma_service.query_user_profile(user_id, "skills", n_results=1)
        user_skills = set()
        if user_profile:
            # Extract skills from profile
            content = user_profile[0].get('content', '').lower()
            user_skills = set(content.split())  # Simplified
        
        # Identify gaps
        gaps = []
        for skill, frequency in sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True):
            if skill not in user_skills and frequency >= 3:  # Appears in 3+ opportunities
                gaps.append({
                    'skill': skill,
                    'frequency': frequency,
                    'priority': 'high' if frequency >= 10 else 'medium' if frequency >= 5 else 'low'
                })
        
        return {
            'total_opportunities_analyzed': len(opportunities),
            'skill_gaps_identified': len(gaps),
            'top_gaps': gaps[:10],
            'recommendation': f"Focus on learning {gaps[0]['skill']}" if gaps else "No major gaps identified"
        }
    
    @staticmethod
    async def analyze_network_health(user_id: str) -> Dict:
        """Analyze network composition and health"""
        
        contacts = await supabase_service.get_contacts(user_id, limit=10000)
        
        # Analyze by tags
        all_tags = []
        for contact in contacts:
            all_tags.extend(contact.get('tags', []))
        
        tag_distribution = {}
        for tag in all_tags:
            tag_distribution[tag] = tag_distribution.get(tag, 0) + 1
        
        # Analyze by company
        company_distribution = {}
        for contact in contacts:
            company = contact.get('company', 'Unknown')
            company_distribution[company] = company_distribution.get(company, 0) + 1
        
        # Identify gaps
        gaps = []
        if tag_distribution.get('hiring_manager', 0) < 10:
            gaps.append("Add more hiring managers to network")
        if tag_distribution.get('alumni', 0) < 5:
            gaps.append("Connect with more alumni")
        if len(company_distribution) < 10:
            gaps.append("Diversify company representation")
        
        return {
            'total_contacts': len(contacts),
            'tag_distribution': tag_distribution,
            'top_companies': sorted(company_distribution.items(), key=lambda x: x[1], reverse=True)[:10],
            'network_gaps': gaps,
            'network_health_score': AnalyticsEngine._calculate_network_health(contacts, tag_distribution)
        }
    
    @staticmethod
    def _calculate_network_health(contacts: List[Dict], tag_dist: Dict) -> int:
        """Calculate network health score (1-10)"""
        score = 5
        
        # Reward diversity
        unique_companies = len(set(c.get('company') for c in contacts if c.get('company')))
        if unique_companies > 20:
            score += 2
        elif unique_companies > 10:
            score += 1
        
        # Reward quality contacts
        high_quality = len([c for c in contacts if c.get('quality_score', 0) >= 7])
        if high_quality > 20:
            score += 2
        elif high_quality > 10:
            score += 1
        
        # Check balance
        if tag_dist.get('hiring_manager', 0) > 5:
            score += 1
        
        return min(max(score, 1), 10)
    
    @staticmethod
    async def get_goal_progress(user_id: str) -> List[Dict]:
        """Track progress toward user goals"""
        
        # Get user profile
        profile_results = chroma_service.query_user_profile(user_id, "goals", n_results=10)
        
        goals = []
        for result in profile_results:
            metadata = result.get('metadata', {})
            if metadata.get('type') == 'goal':
                goal_text = result.get('content', '')
                
                # Calculate progress based on metrics
                # This is simplified - in production, use more sophisticated tracking
                goals.append({
                    'goal': goal_text,
                    'priority': metadata.get('priority', 'medium'),
                    'deadline': metadata.get('deadline', ''),
                    'progress': 0,  # Calculate based on actual metrics
                    'status': 'on_track'
                })
        
        return goals


# Singleton instance
analytics_engine = AnalyticsEngine()
