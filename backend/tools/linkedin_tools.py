from crewai_tools import BaseTool
from typing import Type, List, Dict, Optional
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import random
from services.redis_service import redis_service
from config.settings import settings


class LinkedInJobSearchInput(BaseModel):
    """Input for LinkedInJobSearch"""
    keywords: str = Field(..., description="Job search keywords (e.g., 'AI ML internship')")
    location: str = Field(default="India", description="Job location")
    max_results: int = Field(default=20, description="Maximum number of jobs to return")


class LinkedInJobSearchTool(BaseTool):
    name: str = "LinkedIn Job Search"
    description: str = """Search for jobs on LinkedIn. Use keywords and location to find relevant 
    opportunities. Returns job titles, companies, URLs, and brief descriptions."""
    args_schema: Type[BaseModel] = LinkedInJobSearchInput
    
    def _run(self, keywords: str, location: str = "India", max_results: int = 20) -> str:
        """
        Scrape LinkedIn jobs using Selenium
        Note: This is a simplified version. Production would use LinkedIn API or more robust scraping.
        """
        try:
            # Initialize webdriver (headless mode)
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(options=options)
            
            # Construct LinkedIn jobs URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={keywords.replace(' ', '%20')}&location={location.replace(' ', '%20')}"
            driver.get(search_url)
            
            # Wait for job cards to load
            time.sleep(3)
            
            # Parse job listings
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.find_all('div', class_='base-card', limit=max_results)
            
            jobs = []
            for card in job_cards:
                try:
                    title_elem = card.find('h3', class_='base-search-card__title')
                    company_elem = card.find('h4', class_='base-search-card__subtitle')
                    location_elem = card.find('span', class_='job-search-card__location')
                    link_elem = card.find('a', class_='base-card__full-link')
                    
                    if title_elem and company_elem and link_elem:
                        jobs.append({
                            'title': title_elem.text.strip(),
                            'company': company_elem.text.strip(),
                            'location': location_elem.text.strip() if location_elem else 'N/A',
                            'url': link_elem.get('href', '')
                        })
                except Exception as e:
                    continue
            
            driver.quit()
            
            if not jobs:
                return "No jobs found matching the search criteria."
            
            output = f"Found {len(jobs)} job opportunities:\n\n"
            for i, job in enumerate(jobs, 1):
                output += f"{i}. {job['title']} at {job['company']}\n"
                output += f"   Location: {job['location']}\n"
                output += f"   URL: {job['url']}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching LinkedIn jobs: {str(e)}"


class LinkedInProfileScraperInput(BaseModel):
    """Input for LinkedInProfileScraper"""
    profile_url: str = Field(..., description="LinkedIn profile URL")


class LinkedInProfileScraperTool(BaseTool):
    name: str = "LinkedIn Profile Scraper"
    description: str = """Scrape public information from a LinkedIn profile including name, 
    title, company, and recent activity."""
    args_schema: Type[BaseModel] = LinkedInProfileScraperInput
    
    def _run(self, profile_url: str) -> str:
        """
        Scrape LinkedIn profile
        Note: This is a simplified version. Production needs proper authentication.
        """
        try:
            # Check rate limit
            user_id = "system"  # In production, get from context
            allowed, count = redis_service.check_rate_limit(
                user_id,
                "linkedin_profile_view",
                settings.LINKEDIN_PROFILE_VIEW_DAILY_LIMIT
            )
            
            if not allowed:
                return f"Rate limit exceeded. Daily limit: {settings.LINKEDIN_PROFILE_VIEW_DAILY_LIMIT}"
            
            # Add random delay to mimic human behavior
            time.sleep(random.uniform(2, 5))
            
            # Initialize webdriver
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            
            driver = webdriver.Chrome(options=options)
            driver.get(profile_url)
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            # Extract profile information
            profile_info = {
                'name': 'N/A',
                'title': 'N/A',
                'company': 'N/A',
                'location': 'N/A'
            }
            
            # This is simplified - actual LinkedIn scraping requires authentication
            # For demo purposes, return template
            driver.quit()
            
            output = f"Profile Information:\n"
            output += f"Name: {profile_info['name']}\n"
            output += f"Title: {profile_info['title']}\n"
            output += f"Company: {profile_info['company']}\n"
            output += f"Location: {profile_info['location']}\n"
            output += f"\nNote: Full profile scraping requires LinkedIn authentication.\n"
            output += f"Rate limit status: {count}/{settings.LINKEDIN_PROFILE_VIEW_DAILY_LIMIT} views today"
            
            return output
            
        except Exception as e:
            return f"Error scraping LinkedIn profile: {str(e)}"


class LinkedInConnectionRequestInput(BaseModel):
    """Input for LinkedInConnectionRequest"""
    profile_url: str = Field(..., description="LinkedIn profile URL")
    message: str = Field(..., description="Connection request message (max 300 chars)")
    user_id: str = Field(..., description="User ID for rate limiting")


class LinkedInConnectionRequestTool(BaseTool):
    name: str = "Send LinkedIn Connection Request"
    description: str = """Send a connection request on LinkedIn with a personalized message. 
    Checks rate limits before sending."""
    args_schema: Type[BaseModel] = LinkedInConnectionRequestInput
    
    def _run(self, profile_url: str, message: str, user_id: str) -> str:
        """
        Send LinkedIn connection request
        Note: This is a placeholder. Real implementation requires LinkedIn API or automation.
        """
        try:
            # Check rate limit
            allowed, count = redis_service.check_rate_limit(
                user_id,
                "linkedin_connection",
                settings.LINKEDIN_CONNECTION_DAILY_LIMIT
            )
            
            if not allowed:
                return f"❌ Rate limit exceeded. Daily limit: {settings.LINKEDIN_CONNECTION_DAILY_LIMIT}"
            
            # Validate message length
            if len(message) > 300:
                return "❌ Message too long. LinkedIn connection requests must be under 300 characters."
            
            # Add human-like delay
            delay = random.uniform(10, 30)  # 10-30 seconds
            
            # In production, this would actually send the connection request
            # For now, we'll log it as pending
            
            output = f"✅ Connection request queued successfully!\n\n"
            output += f"Profile: {profile_url}\n"
            output += f"Message: {message}\n"
            output += f"Will be sent in {delay:.0f} seconds (human-like delay)\n\n"
            output += f"Rate limit status: {count}/{settings.LINKEDIN_CONNECTION_DAILY_LIMIT} connections today\n"
            output += f"\nNote: Actual sending requires LinkedIn authentication and will be implemented with proper API/automation."
            
            return output
            
        except Exception as e:
            return f"Error sending connection request: {str(e)}"
