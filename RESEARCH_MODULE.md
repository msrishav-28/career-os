# Research Internship Module - CareerOS

## Overview

The Research Module extends CareerOS to support **research internship campaigns**, enabling automated discovery and personalized outreach to academic researchers and professors. This module was designed based on the comprehensive analysis in `plan2.md`.

## What's New

### 🎓 Academic Discovery
- **Google Scholar Integration**: Find researchers, publications, citations, and research interests
- **arXiv Search**: Discover recent papers and preprints
- **University Faculty Scraping**: Extract researcher information from university department pages
- **Research Match Scoring**: Intelligent scoring algorithm to match researchers with your interests

### 📧 Academic Outreach
- **Publication-Based Personalization**: Reference specific papers and technical details
- **Research-Specific Templates**: Optimized for academic communication style
- **Higher Quality Bar**: 80/100 minimum score (vs 70/100 for industry)
- **Technical Depth Validation**: Ensures genuine understanding of research

### 🗂️ Enhanced Models
- **New Campaign Type**: `RESEARCH` for research internship campaigns
- **New Contact Type**: `RESEARCHER` for academic contacts
- **Research Fields**: `lab_url`, `research_areas`, `publications` in Contact model

## Architecture

```
Research Module Components:
├── Tools (backend/tools/academic_tools.py)
│   ├── GoogleScholarTool
│   ├── ArXivSearchTool
│   ├── UniversityFacultyScraperTool
│   └── ResearchMatchScoringTool
├── Agents (backend/agents/)
│   ├── create_research_discovery_agent()
│   └── Research-specific outreach functions
├── Models (backend/models/)
│   ├── CampaignType.RESEARCH
│   └── ContactType.RESEARCHER
└── Prompts (backend/config/prompts.py)
    ├── RESEARCH_DISCOVERY_PROMPT
    ├── RESEARCH_OUTREACH_CRITERIA
    ├── RESEARCH_EMAIL_TEMPLATE
    └── RESEARCH_MATCH_CRITERIA
```

## Quick Start

### 1. Install Dependencies

```bash
pip install scholarly==1.7.11 arxiv==2.1.0
```

### 2. Create a Research Campaign

```python
from backend.models.campaign import Campaign, CampaignType

campaign = Campaign(
    user_id=user_id,
    name="Summer 2025 Research Internships",
    campaign_type=CampaignType.RESEARCH,
    target_persona="ML/CV researchers at top universities",
    metadata={
        "research_interests": ["computer vision", "deep learning", "self-supervised learning"],
        "target_universities": ["Stanford", "MIT", "Berkeley", "CMU"],
        "timeline": "Summer 2025",
        "duration": "10-12 weeks"
    },
    daily_outreach_limit=10,
    min_personalization_score=80  # Higher bar for research
)
```

### 3. Discover Researchers

```python
from backend.agents.discovery_agent import create_research_discovery_agent, create_researcher_discovery_prompt

# Create agent
agent = create_research_discovery_agent()

# Generate discovery prompt
prompt = create_researcher_discovery_prompt(
    research_interests=["computer vision", "self-supervised learning"],
    target_universities=["Stanford", "MIT", "Berkeley"],
    user_background={
        "level": "Undergraduate senior",
        "experience": "2 years ML research, published at local conference"
    }
)

# Run discovery
researchers = agent.execute(prompt)
```

### 4. Generate Research Outreach

```python
from backend.agents.outreach_agent import create_research_outreach_prompt

researcher = {
    "name": "Dr. Jane Smith",
    "affiliation": "Stanford University",
    "research_areas": ["computer vision", "self-supervised learning"],
    "publications": [
        {
            "title": "Self-Supervised Learning with Momentum Encoders",
            "year": "2024",
            "citation": "Smith et al., CVPR 2024"
        }
    ],
    "lab_url": "https://example.stanford.edu/vision-lab"
}

user_profile = {
    "name": "Your Name",
    "affiliation": "XYZ University",
    "research_interests": ["computer vision", "domain adaptation"],
    "projects": ["Medical Image Classification", "Self-Supervised Pretraining"],
    "technical_skills": "PyTorch, CNNs, Transformers"
}

campaign_context = {
    "timeline": "Summer 2025",
    "duration": "10-12 weeks",
    "goals": "Gain research experience in computer vision"
}

prompt = create_research_outreach_prompt(researcher, user_profile, campaign_context)
```

## Key Differences from Industry Outreach

| Aspect | Industry Outreach | Research Outreach |
|--------|------------------|-------------------|
| **Minimum Score** | 70/100 | 80/100 |
| **Email Length** | 150-300 words | 150-200 words (more concise) |
| **Key Requirement** | Show relevant experience | Reference specific publications |
| **Technical Depth** | Optional | Required |
| **Call-to-Action** | Ask for interview/call | Inquire about research opportunities |
| **Timeline** | Flexible | Specific (Summer 2025, etc.) |
| **Attachments** | Resume/portfolio | CV + research statement |

## Quality Criteria for Research Emails

### Academic Specificity (30 points)
- ✅ Reference specific recent paper by title
- ✅ Mention specific methodology or finding
- ✅ Show technical understanding

### Technical Credibility (25 points)
- ✅ Demonstrate YOUR relevant technical background
- ✅ Reference YOUR related project/research
- ✅ Include quantitative results if applicable

### Clear Research Fit (20 points)
- ✅ Explain WHY their lab specifically
- ✅ Connect your interests to their current work
- ✅ Show you know their research direction

### Appropriate Length (10 points)
- ✅ 150-200 words (concise but substantive)
- ✅ Every sentence adds value

### Respectful Ask (15 points)
- ✅ Ask about research opportunities (not "give me internship")
- ✅ Mention timeline (Summer 2025, etc.)
- ✅ Offer to share CV/research statement

## Example Research Email

### ❌ Bad Example
```
Subject: Internship Opportunity

Dear Professor Smith,

I read your papers and find them interesting. I am a student interested in ML 
and computer vision. Do you have any internship opportunities for summer?

Best regards,
Student
```

### ✅ Good Example
```
Subject: Research Internship Inquiry - Self-Supervised Learning

Dear Professor Smith,

I read your recent CVPR paper on self-supervised learning with momentum encoders. 
Your approach to handling distribution shift particularly resonated with my work 
on domain adaptation for medical imaging. I implemented a similar contrastive 
framework and achieved 12% improvement on our chest X-ray dataset.

I'm exploring research internships for Summer 2025 (10-12 weeks) and would love 
to discuss potential opportunities in your lab. I've attached my CV and would be 
happy to share more details about my background.

Best regards,
[Your Name]
[Your University]
```

## Research Tools Reference

### GoogleScholarTool
```python
tool = GoogleScholarTool()
result = tool._run("Jane Smith Stanford")

# Returns:
{
    'found': True,
    'name': 'Jane Smith',
    'affiliation': 'Stanford University',
    'interests': ['computer vision', 'machine learning'],
    'citations': {
        'total': 5234,
        'h_index': 28,
        'i10_index': 45
    },
    'publications': [
        {
            'title': '...',
            'year': '2024',
            'citations': 150
        }
    ]
}
```

### ArXivSearchTool
```python
tool = ArXivSearchTool()
papers = tool._run("au:Jane Smith AND cat:cs.CV", max_results=5)

# Returns list of recent papers
```

### UniversityFacultyScraperTool
```python
tool = UniversityFacultyScraperTool()
faculty = tool._run("https://cs.stanford.edu/directory/faculty")

# Returns list of faculty with names, emails, research areas
```

### ResearchMatchScoringTool
```python
tool = ResearchMatchScoringTool()
result = tool._run(researcher_profile, user_interests)

# Returns:
{
    'score': 8,  # out of 10
    'reasons': [
        'Shared research interests: 2 overlaps',
        'Active researcher with recent publications',
        'Well-cited researcher'
    ],
    'recommendation': 'High match'
}
```

## Best Practices

### 1. Research Discovery
- ✅ Start with top target universities
- ✅ Focus on quality over quantity (20-30 excellent matches > 100 mediocre)
- ✅ Verify recent publications (last 2 years)
- ✅ Check for active lab websites
- ✅ Prioritize researchers with 10-30 h-index (senior enough to mentor, junior enough to respond)

### 2. Outreach Timing
- ✅ Send Tuesday-Thursday, 9-11 AM (when professors check email)
- ✅ Avoid Mondays (email overload) and Fridays (weekend mode)
- ✅ Send in September-November for summer positions
- ✅ Follow up after 7-10 days (academics slower to respond than industry)

### 3. Email Quality
- ✅ Always reference a specific publication (by exact title)
- ✅ Mention technical details (methodology, findings, dataset)
- ✅ Connect to YOUR concrete project (with quantitative results)
- ✅ Keep under 200 words
- ✅ Attach CV (always) and research statement (if you have one)

### 4. Response Handling
- ✅ Respond within 24 hours to positive replies
- ✅ Be flexible on call timing (professors have busy schedules)
- ✅ Prepare technical questions about their research
- ✅ Have your CV and research statement ready to share

## Scoring Examples

### Example 1: Low Score (55/100)
```
Dear Professor Smith,

I am interested in computer vision and would like to work in your lab 
for the summer. I have taken courses in ML and have done some projects.

Please let me know if you have any openings.
```

**Issues:**
- ❌ No specific paper reference (0/30 for academic specificity)
- ❌ Generic project mention (5/25 for technical credibility)
- ❌ No clear research fit explained (5/20)
- ❌ Too short, lacks substance (5/10 for length)

---

### Example 2: Excellent Score (92/100)
```
Dear Professor Smith,

I read your NeurIPS 2024 paper on contrastive learning for medical imaging. 
Your use of momentum-based encoders to handle class imbalance inspired my 
recent work on chest X-ray classification, where I implemented a similar 
approach and improved F1-score by 15% on the ChestX-ray14 dataset.

I'm particularly interested in your lab's focus on self-supervised pretraining 
for low-resource medical domains. My undergraduate thesis explores this exact 
problem for dermatology imaging. I'm seeking research internships for Summer 
2025 (10-12 weeks) and would love to discuss opportunities.

I've attached my CV and can share my thesis draft. Would you be available 
for a brief call?

Best regards,
[Name]
[University]
```

**Strengths:**
- ✅ Specific paper with technical detail (28/30)
- ✅ Concrete project with quantitative result (24/25)
- ✅ Clear research fit and lab focus (20/20)
- ✅ Perfect length and substance (10/10)
- ✅ Respectful ask with timeline (10/15)

## Integration with Existing CareerOS

The research module seamlessly integrates with your existing CareerOS:

1. **Multi-Campaign System**: Run research + industry campaigns simultaneously
2. **Unified CRM**: Track all contacts (researchers + industry) in one place
3. **Shared Infrastructure**: Uses same database, API, and agent framework
4. **Analytics Dashboard**: View research campaign metrics alongside industry

## Troubleshooting

### Google Scholar Rate Limiting
```python
# Option 1: Add delays between requests
import time
time.sleep(5)

# Option 2: Use proxy (in academic_tools.py)
from scholarly import ProxyGenerator
pg = ProxyGenerator()
scholarly.use_proxy(pg)
```

### University Scraper Not Working
- Different universities have different HTML structures
- Customize the scraper for your target universities
- Check `UniversityFacultyScraperTool` in `academic_tools.py`

### Low Personalization Scores
- Ensure researcher profile includes publications
- Verify user profile has concrete projects
- Check that research areas overlap
- Use `calculate_research_personalization_score()` for debugging

## Future Enhancements

### Phase 1 (Current)
- ✅ Google Scholar integration
- ✅ arXiv search
- ✅ Basic university scraping
- ✅ Research match scoring
- ✅ Academic email templates

### Phase 2 (Planned)
- 🔲 Pre-built researcher database (10,000+ researchers)
- 🔲 Semantic Scholar API integration
- 🔲 Grant tracking (NSF, NIH awards)
- 🔲 Lab size estimation
- 🔲 PhD student profiles (potential mentors)

### Phase 3 (Future)
- 🔲 Conference paper tracking (auto-discover new researchers)
- 🔲 Twitter/X academic engagement
- 🔲 ResearchGate integration
- 🔲 Citation network analysis
- 🔲 Lab culture insights (from alumni)

## Competitive Advantage

Your CareerOS now has:

| Feature | Their System | Your CareerOS |
|---------|-------------|---------------|
| Research internships | ✅ Yes | ✅ Yes |
| Industry internships | ❌ No | ✅ Yes |
| Multi-campaign | ❌ No | ✅ Yes |
| CRM tracking | ❌ No | ✅ Yes |
| Response handling | ❌ No | ✅ Yes |
| Startup validation | ❌ No | ✅ Yes |
| LinkedIn networking | ❌ No | ✅ Yes |
| Open source | ❌ No | ✅ Yes |

**You're building something MORE valuable and versatile.**

## Support

For issues or questions:
1. Check the code in `backend/tools/academic_tools.py`
2. Review prompts in `backend/config/prompts.py`
3. Test with example researchers first
4. Adjust scoring thresholds in campaign settings

## Contributing

To extend the research module:
1. Add new academic data sources (Semantic Scholar, PubMed, etc.)
2. Improve university scraping for specific institutions
3. Enhance match scoring algorithm
4. Add more research-specific templates

---

**Built with plan2.md specifications | Integrated into CareerOS**
