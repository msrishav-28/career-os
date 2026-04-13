import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import uuid
from config.settings import settings


class ChromaDBService:
    """Service for managing ChromaDB vector database operations"""
    
    def __init__(self):
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=settings.CHROMA_PERSIST_DIR
        ))
        self.collections = {}
    
    def get_or_create_collection(self, collection_name: str, metadata: Dict = None):
        """Get or create a ChromaDB collection"""
        if collection_name not in self.collections:
            self.collections[collection_name] = self.client.get_or_create_collection(
                name=collection_name,
                metadata=metadata or {}
            )
        return self.collections[collection_name]
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """Add documents to a collection"""
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def query_documents(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """Query documents from a collection"""
        collection = self.get_or_create_collection(collection_name)
        
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where
        )
        return results
    
    def update_document(
        self,
        collection_name: str,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Update a document in a collection"""
        collection = self.get_or_create_collection(collection_name)
        
        update_data = {"ids": [document_id]}
        if document:
            update_data["documents"] = [document]
        if metadata:
            update_data["metadatas"] = [metadata]
        
        collection.update(**update_data)
    
    def delete_documents(self, collection_name: str, ids: List[str]):
        """Delete documents from a collection"""
        collection = self.get_or_create_collection(collection_name)
        collection.delete(ids=ids)
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get number of documents in a collection"""
        collection = self.get_or_create_collection(collection_name)
        return collection.count()
    
    # User Profile Memory Methods
    def store_user_profile(self, user_id: str, profile_data: Dict):
        """Store user profile in vector database"""
        collection_name = f"user_profile_{user_id}"
        
        documents = []
        metadatas = []
        
        # Store skills
        if profile_data.get("skills"):
            doc = f"User skills: {', '.join(profile_data['skills'])}"
            documents.append(doc)
            metadatas.append({"type": "skills", "category": "technical"})
        
        # Store projects
        for project in profile_data.get("projects", []):
            doc = f"Project: {project.get('name', '')}. {project.get('description', '')}. Tech: {project.get('tech_stack', '')}"
            documents.append(doc)
            metadatas.append({
                "type": "project",
                "name": project.get("name", ""),
                "url": project.get("url", "")
            })
        
        # Store experiences
        for exp in profile_data.get("experiences", []):
            doc = f"Experience: {exp.get('title', '')} at {exp.get('company', '')}. {exp.get('description', '')}"
            documents.append(doc)
            metadatas.append({
                "type": "experience",
                "company": exp.get("company", ""),
                "title": exp.get("title", "")
            })
        
        # Store goals
        for goal in profile_data.get("goals", []):
            doc = f"Career goal: {goal.get('goal', '')}. Priority: {goal.get('priority', 'medium')}"
            documents.append(doc)
            metadatas.append({
                "type": "goal",
                "priority": goal.get("priority", "medium"),
                "deadline": goal.get("deadline", "")
            })
        
        if documents:
            self.add_documents(collection_name, documents, metadatas)
    
    def query_user_profile(self, user_id: str, query: str, n_results: int = 5) -> List[Dict]:
        """Query user profile memory"""
        collection_name = f"user_profile_{user_id}"
        
        try:
            results = self.query_documents(collection_name, query, n_results)
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "content": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
            
            return formatted_results
        except Exception as e:
            print(f"Error querying profile: {e}")
            return []
    
    # Outreach Templates Memory
    def store_successful_template(
        self,
        user_id: str,
        message: str,
        response_rate: float,
        template_type: str,
        persona: str
    ):
        """Store successful outreach template"""
        collection_name = f"outreach_templates_{user_id}"
        
        metadata = {
            "response_rate": response_rate,
            "template_type": template_type,
            "persona": persona,
            "success": True
        }
        
        self.add_documents(collection_name, [message], [metadata])
    
    def get_similar_templates(
        self,
        user_id: str,
        context: str,
        persona: str,
        n_results: int = 3
    ) -> List[Dict]:
        """Get similar successful templates"""
        collection_name = f"outreach_templates_{user_id}"
        
        try:
            results = self.query_documents(
                collection_name,
                context,
                n_results,
                where={"persona": persona}
            )
            
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "template": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
            
            return formatted_results
        except Exception:
            return []
    
    # Network Intelligence
    def store_network_insight(self, user_id: str, insight: str, metadata: Dict):
        """Store network intelligence insight"""
        collection_name = f"network_knowledge_{user_id}"
        self.add_documents(collection_name, [insight], [metadata])
    
    def query_network_knowledge(self, user_id: str, query: str, n_results: int = 5) -> List[Dict]:
        """Query network intelligence"""
        collection_name = f"network_knowledge_{user_id}"
        
        try:
            results = self.query_documents(collection_name, query, n_results)
            
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    "insight": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i]
                })
            
            return formatted_results
        except Exception:
            return []


# Singleton instance
chroma_service = ChromaDBService()
