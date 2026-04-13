from crewai_tools import BaseTool
from typing import Type, List, Dict
from pydantic import BaseModel, Field
from services.chromadb_service import chroma_service


class ProfileQueryInput(BaseModel):
    """Input for ProfileQueryTool"""
    user_id: str = Field(..., description="The user ID")
    query: str = Field(..., description="The search query for the user's profile")
    n_results: int = Field(default=5, description="Number of results to return")


class ProfileQueryTool(BaseTool):
    name: str = "Query User Profile"
    description: str = """Use this tool to search the user's profile memory for relevant skills, 
    projects, experiences, or goals. Provide a natural language query about what you're looking for.
    Example: 'What machine learning projects has the user built?'"""
    args_schema: Type[BaseModel] = ProfileQueryInput
    
    def _run(self, user_id: str, query: str, n_results: int = 5) -> str:
        results = chroma_service.query_user_profile(user_id, query, n_results)
        
        if not results:
            return "No relevant information found in user profile."
        
        output = f"Found {len(results)} relevant items from user profile:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['content']}\n"
            output += f"   Type: {result['metadata'].get('type', 'unknown')}\n\n"
        
        return output


class StoreProfileInput(BaseModel):
    """Input for StoreProfileTool"""
    user_id: str = Field(..., description="The user ID")
    profile_data: dict = Field(..., description="User profile data to store")


class StoreProfileTool(BaseTool):
    name: str = "Store User Profile"
    description: str = """Store user profile information (skills, projects, experiences, goals) 
    in the vector database for future retrieval."""
    args_schema: Type[BaseModel] = StoreProfileInput
    
    def _run(self, user_id: str, profile_data: dict) -> str:
        try:
            chroma_service.store_user_profile(user_id, profile_data)
            return f"Successfully stored profile data for user {user_id}"
        except Exception as e:
            return f"Error storing profile: {str(e)}"


class TemplateQueryInput(BaseModel):
    """Input for TemplateQueryTool"""
    user_id: str = Field(..., description="The user ID")
    context: str = Field(..., description="Context for finding similar templates")
    persona: str = Field(..., description="Target persona (e.g., 'hiring_manager', 'student')")
    n_results: int = Field(default=3, description="Number of templates to return")


class TemplateQueryTool(BaseTool):
    name: str = "Get Similar Outreach Templates"
    description: str = """Retrieve successful outreach templates similar to the current context. 
    Useful for learning from past successful messages."""
    args_schema: Type[BaseModel] = TemplateQueryInput
    
    def _run(self, user_id: str, context: str, persona: str, n_results: int = 3) -> str:
        results = chroma_service.get_similar_templates(user_id, context, persona, n_results)
        
        if not results:
            return f"No similar templates found for persona '{persona}'."
        
        output = f"Found {len(results)} similar successful templates:\n\n"
        for i, result in enumerate(results, 1):
            metadata = result['metadata']
            output += f"{i}. Response Rate: {metadata.get('response_rate', 0):.1%}\n"
            output += f"   Type: {metadata.get('template_type', 'unknown')}\n"
            output += f"   Template: {result['template'][:200]}...\n\n"
        
        return output


class NetworkKnowledgeInput(BaseModel):
    """Input for NetworkKnowledgeTool"""
    user_id: str = Field(..., description="The user ID")
    query: str = Field(..., description="Query about network insights")
    n_results: int = Field(default=5, description="Number of insights to return")


class NetworkKnowledgeTool(BaseTool):
    name: str = "Query Network Intelligence"
    description: str = """Search for insights about the user's network, such as engagement patterns, 
    successful strategies, or information about contacts."""
    args_schema: Type[BaseModel] = NetworkKnowledgeInput
    
    def _run(self, user_id: str, query: str, n_results: int = 5) -> str:
        results = chroma_service.query_network_knowledge(user_id, query, n_results)
        
        if not results:
            return "No relevant network insights found."
        
        output = f"Found {len(results)} network insights:\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result['insight']}\n"
            output += f"   Source: {result['metadata'].get('type', 'unknown')}\n\n"
        
        return output
