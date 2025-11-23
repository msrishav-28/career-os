import pytest
from agents import (
    create_profile_agent,
    create_discovery_agent,
    create_outreach_agent,
    create_crm_agent,
    create_growth_agent
)
from agents.outreach_agent import calculate_personalization_score, validate_message_quality
from agents.crm_agent import analyze_response_sentiment, calculate_contact_priority


class TestAgents:
    """Test suite for AI agents"""
    
    def test_profile_agent_creation(self):
        """Test profile agent can be created"""
        agent = create_profile_agent("test-user")
        assert agent is not None
        assert agent.role is not None
    
    def test_discovery_agent_creation(self):
        """Test discovery agent can be created"""
        agent = create_discovery_agent()
        assert agent is not None
        assert agent.role is not None
    
    def test_outreach_agent_creation(self):
        """Test outreach agent can be created"""
        agent = create_outreach_agent()
        assert agent is not None
        assert agent.role is not None
    
    def test_crm_agent_creation(self):
        """Test CRM agent can be created"""
        agent = create_crm_agent()
        assert agent is not None
        assert agent.role is not None
    
    def test_growth_agent_creation(self):
        """Test growth agent can be created"""
        agent = create_growth_agent()
        assert agent is not None
        assert agent.role is not None


class TestPersonalizationScoring:
    """Test personalization scoring logic"""
    
    def test_score_with_high_personalization(self):
        """Test message with high personalization gets good score"""
        message = """Hi John, I saw your recent post about machine learning at Google. 
        I recently built a similar ML pipeline using TensorFlow. Would love to discuss!"""
        
        contact = {
            "name": "John",
            "company": "Google",
            "recent_activity": "post about machine learning"
        }
        
        user_info = {
            "relevant_projects": ["ML pipeline", "TensorFlow"]
        }
        
        result = calculate_personalization_score(message, contact, user_info)
        assert result['score'] >= 70
        assert result['passed'] is True
    
    def test_score_with_low_personalization(self):
        """Test generic message gets low score"""
        message = "Hi, I'd like to connect."
        
        contact = {"name": "John"}
        user_info = {}
        
        result = calculate_personalization_score(message, contact, user_info)
        assert result['score'] < 70
        assert result['passed'] is False
    
    def test_validate_message_quality_with_placeholders(self):
        """Test message validation rejects placeholders"""
        message = "Hi [NAME], I'd like to connect about [TOPIC]."
        
        is_valid, error = validate_message_quality(message)
        assert is_valid is False
        assert "placeholder" in error.lower()
    
    def test_validate_message_quality_too_short(self):
        """Test message validation rejects too short messages"""
        message = "Hi, let's connect."
        
        is_valid, error = validate_message_quality(message)
        assert is_valid is False
        assert "short" in error.lower()


class TestSentimentAnalysis:
    """Test sentiment analysis"""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection"""
        reply = "Yes, I'd love to schedule a call! Let's discuss this further."
        
        result = analyze_response_sentiment(reply)
        assert result['sentiment'] == 'positive'
        assert result['priority'] == 'high'
        assert result['requires_action'] is True
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection"""
        reply = "Not interested. Please don't contact me again."
        
        result = analyze_response_sentiment(reply)
        assert result['sentiment'] == 'negative'
        assert result['priority'] == 'low'
        assert result['requires_action'] is False
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        reply = "Thanks for reaching out. I'll review and get back to you."
        
        result = analyze_response_sentiment(reply)
        assert result['sentiment'] == 'neutral'
        assert result['priority'] == 'medium'


class TestContactPriority:
    """Test contact priority calculation"""
    
    def test_high_priority_contact(self):
        """Test high priority calculation"""
        contact = {
            "quality_score": 8,
            "title": "Hiring Manager",
            "company": "Google"
        }
        messages = [{"status": "replied", "reply_content": "Yes, let's talk!"}]
        
        priority = calculate_contact_priority(contact, messages)
        assert priority >= 8
    
    def test_low_priority_contact(self):
        """Test low priority calculation"""
        contact = {
            "quality_score": 3,
            "title": "Student",
            "company": "Unknown"
        }
        messages = []
        
        priority = calculate_contact_priority(contact, messages)
        assert priority <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
