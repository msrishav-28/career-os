# Research Internship Module

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Scholarly](https://img.shields.io/badge/Scholarly-1.7.11-orange?style=for-the-badge)
![arXiv](https://img.shields.io/badge/arXiv-2.1.0-red?style=for-the-badge)

The Research Module extends CareerOS to support **research internship campaigns**, enabling automated discovery and personalized outreach to academic researchers and professors.

## Features

### Academic Discovery
*   **Google Scholar Integration**: Retrieval of researcher profiles, h-index, and citations.
*   **arXiv Search**: Automated discovery of recent preprints and papers.
*   **Faculty Scraping**: Extraction of contact details from university department pages.
*   **Match Scoring**: Algorithm to quantify alignment between user interests and researcher publications.

### Academic Outreach
*   **Publication-Based Context**: Automatically references specific papers in outreach messages.
*   **Academic Templates**: Tailored for formal academic communication.
*   **Quality Gates**: Enforces a minimum personalization score of 80/100.
*   **Technical Validation**: Ensures messages demonstrate genuine understanding of the research work.

## Architecture

The module consists of four primary components:

1.  **Tools** (`backend/tools/academic_tools.py`)
    *   `GoogleScholarTool`: Wrapper for the scholarly library.
    *   `ArXivSearchTool`: Interface for the arXiv API.
    *   `UniversityFacultyScraperTool`: HTML parser for typical faculty directories.
    *   `ResearchMatchScoringTool`: Utility for calculating research alignment.

2.  **Agents** (`backend/agents/`)
    *   `ResearchDiscoveryAgent`: Specialized agent for executing academic search strategies.

3.  **Models** (`backend/models/`)
    *   `CampaignType.RESEARCH`: Enum extension for research campaigns.
    *   `ContactType.RESEARCHER`: Extension for academic contacts.

4.  **Prompts** (`backend/config/prompts.py`)
    *   Specialized system prompts for academic context generation.

## Usage Guide

### 1. Install Dependencies
```bash
pip install scholarly==1.7.11 arxiv==2.1.0
```

### 2. Configure Campaign
Initialize a campaign with `CampaignType.RESEARCH`:

```python
campaign = Campaign(
    user_id=user_id,
    name="Summer 2025 Research Internships",
    campaign_type=CampaignType.RESEARCH,
    target_persona="ML researchers at top universities",
    metadata={
        "research_interests": ["computer vision", "deep learning"],
        "target_universities": ["Stanford", "MIT", "Berkeley"],
        "timeline": "Summer 2025"
    },
    min_personalization_score=80
)
```

### 3. Execution Flow
1.  **Discovery**: The agent searches selected universities or Google Scholar for researchers matching the interests.
2.  **Scoring**: Each researcher is scored (0-10) based on publication relevance.
3.  **Outreach Generation**: The Outreach Agent generates an email referencing a specific recent paper.
4.  **Review**: The user reviews the draft in the dashboard.
5.  **Delivery**: Approved messages are sent via the configured email provider.

## Best Practices

*   **University Selection**: Start with a focused list of 3-5 universities.
*   **Publication Filter**: Prioritize researchers with publications in the last 2 years.
*   **Timing**: Research outreach is most effective between September and November for summer positions.
*   **Context**: Ensure the user profile contains specific technical projects to increase credibility.
