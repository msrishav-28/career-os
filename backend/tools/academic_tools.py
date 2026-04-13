"""
Academic Research Tools for CareerOS
Includes Google Scholar, arXiv, and university faculty scraping tools
"""

from crewai_tools import BaseTool
from typing import Optional, List, Dict
import arxiv
from scholarly import scholarly, ProxyGenerator
from bs4 import BeautifulSoup
import requests
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class GoogleScholarTool(BaseTool):
    """
    Tool for searching Google Scholar and retrieving researcher publications
    """
    name: str = "Google Scholar Search"
    description: str = """
    Search Google Scholar for researcher publications, citations, and research interests.
    Input should be a researcher's name or specific query.
    Returns: Recent publications, citations, h-index, and research interests.
    """
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _run(self, researcher_name: str) -> Dict:
        """
        Fetch researcher information from Google Scholar
        
        Args:
            researcher_name: Full name of the researcher
            
        Returns:
            Dict containing publications, citations, interests
        """
        try:
            # Setup proxy to avoid rate limiting (optional)
            # pg = ProxyGenerator()
            # scholarly.use_proxy(pg)
            
            # Search for the author
            search_query = scholarly.search_author(researcher_name)
            author = next(search_query, None)
            
            if not author:
                return {
                    'error': f'Researcher "{researcher_name}" not found',
                    'found': False
                }
            
            # Fill author details
            author_detail = scholarly.fill(author)
            
            # Extract publications (limit to top 5 most recent)
            publications = []
            for pub in list(author_detail.get('publications', []))[:5]:
                pub_info = {
                    'title': pub.get('bib', {}).get('title', 'N/A'),
                    'year': pub.get('bib', {}).get('pub_year', 'N/A'),
                    'citation': pub.get('bib', {}).get('citation', 'N/A'),
                    'citations': pub.get('num_citations', 0),
                    'url': pub.get('pub_url', '')
                }
                publications.append(pub_info)
            
            result = {
                'found': True,
                'name': author_detail.get('name', researcher_name),
                'affiliation': author_detail.get('affiliation', 'N/A'),
                'interests': author_detail.get('interests', []),
                'citations': {
                    'total': author_detail.get('citedby', 0),
                    'h_index': author_detail.get('hindex', 0),
                    'i10_index': author_detail.get('i10index', 0)
                },
                'publications': publications,
                'scholar_url': author_detail.get('url_picture', '')
            }
            
            return result
            
        except StopIteration:
            return {
                'error': f'Researcher "{researcher_name}" not found',
                'found': False
            }
        except Exception as e:
            logger.error(f"Error fetching Google Scholar data: {str(e)}")
            return {
                'error': str(e),
                'found': False
            }


class ArXivSearchTool(BaseTool):
    """
    Tool for searching arXiv for academic papers
    """
    name: str = "arXiv Paper Search"
    description: str = """
    Search arXiv for recent academic papers by author, topic, or keyword.
    Returns: Paper titles, abstracts, authors, and publication dates.
    """
    
    def _run(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Search arXiv for papers
        
        Args:
            query: Search query (author name, topic, or keyword)
            max_results: Maximum number of results to return
            
        Returns:
            List of paper details
        """
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in search.results():
                paper_info = {
                    'title': result.title,
                    'authors': [author.name for author in result.authors],
                    'published': result.published.strftime('%Y-%m-%d'),
                    'summary': result.summary[:300] + '...' if len(result.summary) > 300 else result.summary,
                    'pdf_url': result.pdf_url,
                    'categories': result.categories
                }
                papers.append(paper_info)
            
            return papers
            
        except Exception as e:
            logger.error(f"Error searching arXiv: {str(e)}")
            return []


class UniversityFacultyScraperTool(BaseTool):
    """
    Tool for scraping university faculty directories to find researchers
    """
    name: str = "University Faculty Scraper"
    description: str = """
    Scrape university department faculty pages to extract researcher information.
    Input: University department URL (e.g., Stanford CS faculty page)
    Returns: List of faculty members with names, emails, research areas, and lab URLs.
    """
    
    def _run(self, department_url: str) -> List[Dict]:
        """
        Scrape faculty information from university department page
        
        Args:
            department_url: URL of the department faculty page
            
        Returns:
            List of faculty member details
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(department_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            faculty_list = []
            
            # Common patterns for faculty listings
            # This is a generic scraper - may need customization per university
            faculty_sections = soup.find_all(['div', 'li', 'tr'], class_=lambda x: x and any(
                term in str(x).lower() for term in ['faculty', 'person', 'profile', 'member']
            ))
            
            for section in faculty_sections[:50]:  # Limit to 50 to avoid too much data
                # Extract name
                name_tag = section.find(['h2', 'h3', 'h4', 'a', 'span'], class_=lambda x: x and 'name' in str(x).lower())
                if not name_tag:
                    name_tag = section.find('a')
                
                name = name_tag.get_text(strip=True) if name_tag else None
                
                if not name or len(name) < 3:
                    continue
                
                # Extract email
                email_tag = section.find('a', href=lambda x: x and 'mailto:' in x)
                email = email_tag.get('href').replace('mailto:', '') if email_tag else None
                
                # Extract profile/lab URL
                profile_link = section.find('a', href=True)
                profile_url = profile_link.get('href') if profile_link else None
                if profile_url and not profile_url.startswith('http'):
                    profile_url = requests.compat.urljoin(department_url, profile_url)
                
                # Extract research areas (if available)
                research_areas = []
                research_tag = section.find(text=lambda x: x and any(
                    term in str(x).lower() for term in ['research', 'interests', 'areas']
                ))
                if research_tag:
                    research_areas = [area.strip() for area in research_tag.split(',')[:5]]
                
                faculty_info = {
                    'name': name,
                    'email': email,
                    'profile_url': profile_url,
                    'research_areas': research_areas,
                    'source': department_url
                }
                
                faculty_list.append(faculty_info)
            
            # Remove duplicates based on name
            seen_names = set()
            unique_faculty = []
            for faculty in faculty_list:
                if faculty['name'] not in seen_names:
                    seen_names.add(faculty['name'])
                    unique_faculty.append(faculty)
            
            return unique_faculty
            
        except Exception as e:
            logger.error(f"Error scraping faculty page: {str(e)}")
            return []


class ResearchMatchScoringTool(BaseTool):
    """
    Tool for scoring how well a researcher matches user's interests
    """
    name: str = "Research Match Scorer"
    description: str = """
    Score how well a researcher matches the user's research interests and background.
    Input: Researcher profile and user interests
    Returns: Match score (1-10) with reasoning
    """
    
    def _run(self, researcher_profile: Dict, user_interests: List[str]) -> Dict:
        """
        Calculate match score between researcher and user interests
        
        Args:
            researcher_profile: Dict with researcher details (interests, publications)
            user_interests: List of user's research interests
            
        Returns:
            Dict with score and reasoning
        """
        try:
            score = 0
            reasons = []
            
            # Extract researcher interests and recent work
            researcher_interests = researcher_profile.get('interests', [])
            publications = researcher_profile.get('publications', [])
            
            # Convert to lowercase for comparison
            user_interests_lower = [interest.lower() for interest in user_interests]
            researcher_interests_lower = [interest.lower() for interest in researcher_interests]
            
            # Check interest overlap (up to 5 points)
            interest_overlap = len(set(user_interests_lower) & set(researcher_interests_lower))
            if interest_overlap > 0:
                score += min(interest_overlap * 2, 5)
                reasons.append(f"Shared research interests: {interest_overlap} overlaps")
            
            # Check publication recency (up to 2 points)
            recent_pubs = [pub for pub in publications if pub.get('year', '0').isdigit() and int(pub['year']) >= 2022]
            if len(recent_pubs) >= 3:
                score += 2
                reasons.append("Active researcher with recent publications")
            elif len(recent_pubs) >= 1:
                score += 1
                reasons.append("Some recent publications")
            
            # Check citation count (up to 2 points)
            citations = researcher_profile.get('citations', {})
            total_citations = citations.get('total', 0)
            if total_citations > 5000:
                score += 2
                reasons.append("Highly cited researcher")
            elif total_citations > 1000:
                score += 1
                reasons.append("Well-cited researcher")
            
            # Check h-index (up to 1 point)
            h_index = citations.get('h_index', 0)
            if h_index > 20:
                score += 1
                reasons.append(f"Strong h-index: {h_index}")
            
            # Base score for having complete profile
            if researcher_profile.get('affiliation'):
                score += 1
                reasons.append("Has clear affiliation")
            
            return {
                'score': min(score, 10),  # Cap at 10
                'reasons': reasons,
                'recommendation': 'High match' if score >= 7 else 'Medium match' if score >= 5 else 'Low match'
            }
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return {
                'score': 0,
                'reasons': ['Error in calculation'],
                'recommendation': 'Unable to score'
            }
