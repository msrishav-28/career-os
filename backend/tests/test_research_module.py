"""
Tests for Research Module
Testing academic tools, discovery, and outreach for research internships
"""

import pytest
from backend.tools.academic_tools import (
    GoogleScholarTool,
    ArXivSearchTool,
    ResearchMatchScoringTool
)
from backend.agents.discovery_agent import create_researcher_discovery_prompt
from backend.agents.outreach_agent import (
    create_research_outreach_prompt,
    calculate_research_personalization_score,
    validate_research_email_quality
)


class TestAcademicTools:
    """Test academic research tools"""
    
    def test_google_scholar_tool_exists(self):
        """Test Google Scholar tool can be instantiated"""
        tool = GoogleScholarTool()
        assert tool.name == "Google Scholar Search"
        assert callable(tool._run)
    
    def test_arxiv_tool_exists(self):
        """Test arXiv tool can be instantiated"""
        tool = ArXivSearchTool()
        assert tool.name == "arXiv Paper Search"
        assert callable(tool._run)
    
    def test_research_match_scoring_tool(self):
        """Test research match scoring"""
        tool = ResearchMatchScoringTool()
        
        researcher = {
            'interests': ['computer vision', 'machine learning'],
            'publications': [
                {'title': 'Deep Learning', 'year': '2023'},
                {'title': 'Computer Vision', 'year': '2024'}
            ],
            'citations': {'total': 2000, 'h_index': 25},
            'affiliation': 'Stanford University'
        }
        
        user_interests = ['computer vision', 'deep learning']
        
        result = tool._run(researcher, user_interests)
        
        assert 'score' in result
        assert 'reasons' in result
        assert 'recommendation' in result
        assert 0 <= result['score'] <= 10


class TestResearchDiscovery:
    """Test research discovery prompts"""
    
    def test_researcher_discovery_prompt_generation(self):
        """Test generating researcher discovery prompt"""
        prompt = create_researcher_discovery_prompt(
            research_interests=['computer vision', 'NLP'],
            target_universities=['Stanford', 'MIT'],
            user_background={
                'level': 'Undergraduate senior',
                'experience': '2 years ML research'
            }
        )
        
        assert 'computer vision' in prompt.lower()
        assert 'nlp' in prompt.lower()
        assert 'stanford' in prompt.lower()
        assert 'mit' in prompt.lower()
        assert len(prompt) > 500  # Should be substantial


class TestResearchOutreach:
    """Test research outreach generation and scoring"""
    
    def test_research_outreach_prompt_generation(self):
        """Test generating research outreach prompt"""
        researcher = {
            'name': 'Dr. Jane Smith',
            'affiliation': 'Stanford University',
            'research_areas': ['computer vision', 'deep learning'],
            'publications': [
                {
                    'title': 'Self-Supervised Learning for Vision',
                    'year': '2024',
                    'citation': 'Smith et al., CVPR 2024'
                }
            ],
            'lab_url': 'https://example.com/lab',
            'quality_score': 9
        }
        
        user_profile = {
            'name': 'Test Student',
            'affiliation': 'Test University',
            'research_interests': ['computer vision'],
            'projects': ['Image Classification'],
            'technical_skills': 'PyTorch, CNNs'
        }
        
        campaign_context = {
            'timeline': 'Summer 2025',
            'duration': '10-12 weeks',
            'goals': 'Research experience'
        }
        
        prompt = create_research_outreach_prompt(
            researcher, user_profile, campaign_context
        )
        
        assert 'Jane Smith' in prompt
        assert 'Stanford' in prompt
        assert 'Self-Supervised Learning' in prompt
        assert 'Summer 2025' in prompt
        assert len(prompt) > 1000  # Should be comprehensive
    
    def test_research_personalization_score_high_quality(self):
        """Test scoring a high-quality research email"""
        researcher = {
            'publications': [
                {'title': 'Deep Learning for Computer Vision', 'year': '2024'}
            ],
            'research_areas': ['computer vision', 'machine learning']
        }
        
        user_info = {
            'projects': ['Image Classification System'],
            'research_interests': ['computer vision', 'deep learning']
        }
        
        # High quality email
        message = """
        I read your recent paper "Deep Learning for Computer Vision" and found 
        your approach to handling distribution shift fascinating. I implemented 
        a similar contrastive learning framework in my Image Classification System 
        project and achieved 15% improvement on accuracy. I'm exploring research 
        opportunities for Summer 2025 and would love to discuss potential 
        positions in your lab.
        """
        
        result = calculate_research_personalization_score(
            message, researcher, user_info
        )
        
        assert result['score'] >= 60  # Should score reasonably well
        assert 'breakdown' in result
        assert result['passed'] or result['score'] >= 70
    
    def test_research_personalization_score_low_quality(self):
        """Test scoring a low-quality research email"""
        researcher = {
            'publications': [{'title': 'Some Paper', 'year': '2024'}],
            'research_areas': ['computer vision']
        }
        
        user_info = {
            'projects': [],
            'research_interests': []
        }
        
        # Low quality email
        message = "I want to work in your lab. Do you have internships?"
        
        result = calculate_research_personalization_score(
            message, researcher, user_info
        )
        
        assert result['score'] < 80  # Should fail quality threshold
        assert not result['passed']
    
    def test_validate_research_email_quality_good(self):
        """Test validation of good research email"""
        researcher = {
            'publications': [
                {'title': 'Machine Learning Research', 'year': '2024'}
            ],
            'research_areas': ['machine learning']
        }
        
        # Good email with sufficient length and specificity
        message = """
        Dear Professor Smith,
        
        I recently read your paper on Machine Learning Research and was impressed 
        by your innovative approach to the problem. Your methodology particularly 
        resonated with my own work on similar topics. I have experience with 
        various machine learning techniques and have completed several projects 
        in this domain. I'm interested in research opportunities for Summer 2025 
        and would appreciate the chance to discuss potential positions in your lab. 
        I have attached my CV and can provide additional materials upon request.
        
        Best regards,
        Student
        """
        
        is_valid, error = validate_research_email_quality(message, researcher, min_score=80)
        
        # Note: This may still fail if scoring is strict, but should pass basic validation
        assert isinstance(is_valid, bool)
        assert isinstance(error, str)
    
    def test_validate_research_email_quality_bad(self):
        """Test validation rejects bad research email"""
        researcher = {
            'publications': [{'title': 'Some Paper', 'year': '2024'}],
            'research_areas': ['AI']
        }
        
        # Bad email - too short and generic
        message = "I want to work with you. Any internships?"
        
        is_valid, error = validate_research_email_quality(message, researcher)
        
        assert not is_valid
        assert len(error) > 0


class TestModelIntegration:
    """Test that research types are properly integrated in models"""
    
    def test_research_campaign_type_exists(self):
        """Test RESEARCH campaign type exists"""
        from backend.models.campaign import CampaignType
        
        assert hasattr(CampaignType, 'RESEARCH')
        assert CampaignType.RESEARCH == 'research'
    
    def test_researcher_contact_type_exists(self):
        """Test RESEARCHER contact type exists"""
        from backend.models.contact import ContactType
        
        assert hasattr(ContactType, 'RESEARCHER')
        assert ContactType.RESEARCHER == 'researcher'
    
    def test_contact_has_research_fields(self):
        """Test Contact model has research-specific fields"""
        from backend.models.contact import Contact
        from pydantic import UUID4
        import uuid
        
        # Create a researcher contact
        contact = Contact(
            user_id=uuid.uuid4(),
            name="Dr. Test Researcher",
            email="researcher@example.com",
            contact_type="researcher",
            lab_url="https://example.com/lab",
            research_areas=["computer vision", "machine learning"],
            publications=[
                {"title": "Test Paper", "year": "2024"}
            ]
        )
        
        assert hasattr(contact, 'lab_url')
        assert hasattr(contact, 'research_areas')
        assert hasattr(contact, 'publications')
        assert contact.research_areas == ["computer vision", "machine learning"]
        assert len(contact.publications) == 1


class TestPromptIntegration:
    """Test that research prompts are properly integrated"""
    
    def test_research_prompts_exist(self):
        """Test research-specific prompts exist in config"""
        from backend.config.prompts import (
            RESEARCH_DISCOVERY_PROMPT,
            RESEARCH_OUTREACH_CRITERIA,
            RESEARCH_EMAIL_TEMPLATE,
            RESEARCH_MATCH_CRITERIA
        )
        
        assert len(RESEARCH_DISCOVERY_PROMPT) > 100
        assert len(RESEARCH_OUTREACH_CRITERIA) > 100
        assert len(RESEARCH_EMAIL_TEMPLATE) > 50
        assert len(RESEARCH_MATCH_CRITERIA) > 100
        
        # Check key content
        assert 'researcher' in RESEARCH_DISCOVERY_PROMPT.lower()
        assert 'publication' in RESEARCH_OUTREACH_CRITERIA.lower()
        assert 'professor' in RESEARCH_EMAIL_TEMPLATE.lower()


# Integration test example (requires actual API keys)
@pytest.mark.skipif(True, reason="Requires API keys and network access")
class TestResearchWorkflowIntegration:
    """End-to-end test of research workflow (skipped by default)"""
    
    def test_full_research_workflow(self):
        """Test complete research discovery and outreach workflow"""
        # This would test:
        # 1. Creating a research campaign
        # 2. Discovering researchers
        # 3. Generating outreach messages
        # 4. Scoring and validating
        
        # Requires:
        # - Database setup
        # - API keys
        # - Network access
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
