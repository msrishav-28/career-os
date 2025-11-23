from crewai_tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import requests
from datetime import datetime, timedelta


class GitHubRepoSearchInput(BaseModel):
    """Input for GitHub Repository Search"""
    keywords: str = Field(..., description="Search keywords for repositories")
    language: str = Field(default="", description="Programming language filter")
    max_results: int = Field(default=10, description="Maximum number of results")


class GitHubRepoSearchTool(BaseTool):
    name: str = "Search GitHub Repositories"
    description: str = """Search for GitHub repositories by keywords and language. 
    Returns repository names, descriptions, stars, and URLs."""
    args_schema: Type[BaseModel] = GitHubRepoSearchInput
    
    def _run(self, keywords: str, language: str = "", max_results: int = 10) -> str:
        try:
            # Build search query
            query = keywords
            if language:
                query += f" language:{language}"
            
            # GitHub API search
            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            repos = data.get('items', [])
            
            if not repos:
                return "No repositories found matching the criteria."
            
            output = f"Found {len(repos)} repositories:\n\n"
            for i, repo in enumerate(repos, 1):
                output += f"{i}. {repo['full_name']}\n"
                output += f"   ⭐ {repo['stargazers_count']:,} stars\n"
                output += f"   Description: {repo['description'] or 'No description'}\n"
                output += f"   URL: {repo['html_url']}\n"
                output += f"   Language: {repo['language'] or 'N/A'}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error searching GitHub: {str(e)}"


class GitHubContributorsInput(BaseModel):
    """Input for GitHub Contributors"""
    repo_owner: str = Field(..., description="Repository owner username")
    repo_name: str = Field(..., description="Repository name")
    max_contributors: int = Field(default=10, description="Maximum number of contributors")


class GitHubContributorsTool(BaseTool):
    name: str = "Get GitHub Repository Contributors"
    description: str = """Get top contributors for a GitHub repository. Useful for finding 
    people to connect with in specific technical domains."""
    args_schema: Type[BaseModel] = GitHubContributorsInput
    
    def _run(self, repo_owner: str, repo_name: str, max_contributors: int = 10) -> str:
        try:
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors"
            params = {'per_page': max_contributors}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            contributors = response.json()
            
            if not contributors:
                return "No contributors found."
            
            output = f"Top {len(contributors)} contributors to {repo_owner}/{repo_name}:\n\n"
            for i, contributor in enumerate(contributors, 1):
                output += f"{i}. {contributor['login']}\n"
                output += f"   Contributions: {contributor['contributions']}\n"
                output += f"   Profile: {contributor['html_url']}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error fetching contributors: {str(e)}"


class GitHubUserActivityInput(BaseModel):
    """Input for GitHub User Activity"""
    username: str = Field(..., description="GitHub username")


class GitHubUserActivityTool(BaseTool):
    name: str = "Get GitHub User Activity"
    description: str = """Get recent activity for a GitHub user including repositories, 
    contributions, and activity summary. Useful for researching potential contacts."""
    args_schema: Type[BaseModel] = GitHubUserActivityInput
    
    def _run(self, username: str) -> str:
        try:
            # Get user profile
            user_url = f"https://api.github.com/users/{username}"
            user_response = requests.get(user_url)
            user_response.raise_for_status()
            user_data = user_response.json()
            
            # Get recent repos
            repos_url = f"https://api.github.com/users/{username}/repos"
            repos_response = requests.get(repos_url, params={'sort': 'updated', 'per_page': 5})
            repos_response.raise_for_status()
            repos = repos_response.json()
            
            output = f"GitHub Profile: {username}\n\n"
            output += f"Name: {user_data.get('name', 'N/A')}\n"
            output += f"Bio: {user_data.get('bio', 'No bio')}\n"
            output += f"Location: {user_data.get('location', 'N/A')}\n"
            output += f"Public Repos: {user_data.get('public_repos', 0)}\n"
            output += f"Followers: {user_data.get('followers', 0)}\n"
            output += f"Profile: {user_data.get('html_url')}\n\n"
            
            if repos:
                output += f"Recent Repositories:\n"
                for i, repo in enumerate(repos[:5], 1):
                    output += f"{i}. {repo['name']}\n"
                    output += f"   Stars: {repo['stargazers_count']}\n"
                    output += f"   Language: {repo['language'] or 'N/A'}\n"
                    output += f"   Updated: {repo['updated_at'][:10]}\n"
            
            return output
            
        except Exception as e:
            return f"Error fetching GitHub user activity: {str(e)}"


class GitHubTrendingReposInput(BaseModel):
    """Input for GitHub Trending"""
    language: str = Field(default="", description="Programming language filter")
    since: str = Field(default="daily", description="Time range: daily, weekly, monthly")


class GitHubTrendingReposTool(BaseTool):
    name: str = "Get GitHub Trending Repositories"
    description: str = """Get trending repositories on GitHub for a specific language and time range. 
    Useful for discovering hot projects and potential contacts."""
    args_schema: Type[BaseModel] = GitHubTrendingReposInput
    
    def _run(self, language: str = "", since: str = "daily") -> str:
        try:
            # Calculate date based on 'since' parameter
            if since == "daily":
                date_filter = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            elif since == "weekly":
                date_filter = (datetime.now() - timedelta(weeks=1)).strftime("%Y-%m-%d")
            else:  # monthly
                date_filter = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            # Search for recently created repos with high stars
            query = f"created:>{date_filter}"
            if language:
                query += f" language:{language}"
            
            url = "https://api.github.com/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            repos = data.get('items', [])
            
            if not repos:
                return f"No trending repositories found for {language or 'all languages'}"
            
            output = f"Trending repositories ({since}):\n\n"
            for i, repo in enumerate(repos, 1):
                output += f"{i}. {repo['full_name']}\n"
                output += f"   ⭐ {repo['stargazers_count']:,} stars\n"
                output += f"   Description: {repo['description'] or 'No description'}\n"
                output += f"   Language: {repo['language'] or 'N/A'}\n"
                output += f"   URL: {repo['html_url']}\n\n"
            
            return output
            
        except Exception as e:
            return f"Error fetching trending repos: {str(e)}"
