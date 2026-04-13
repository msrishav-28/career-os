import uuid
from typing import List, Dict, Optional
import os
from config.settings import settings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_openai import OpenAIEmbeddings

class VectorDBService:
    """Service for managing pgvector database operations via Langchain"""
    
    def __init__(self):
        # PGVector requires synchronous engine driver like psycopg2
        raw_url = settings.DATABASE_URL or ""
        
        # Format the URL for psycopg2
        if raw_url.startswith("postgresql+asyncpg://"):
            self.connection_string = raw_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        elif raw_url.startswith("postgres://"):
            self.connection_string = raw_url.replace("postgres://", "postgresql://", 1)
        else:
            self.connection_string = raw_url

        # Check for OpenAI key, throw warning if running locally without it but don't crash
        # (It will crash on first call if key is invalid, which is expected)
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small", 
            api_key=settings.OPENAI_API_KEY or "dummy_key_to_allow_init"
        )
        
        self.stores = {}
    
    def _get_store(self, collection_name: str) -> PGVector:
        """Get or initialize a PGVector store for a specific collection"""
        if collection_name not in self.stores:
            self.stores[collection_name] = PGVector(
                connection_string=self.connection_string,
                embedding_function=self.embeddings,
                collection_name=collection_name,
                use_jsonb=True
            )
        return self.stores[collection_name]
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """Add documents to a collection"""
        store = self._get_store(collection_name)
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        store.add_texts(
            texts=documents,
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
        store = self._get_store(collection_name)
        
        # PGVector using Langchain returns Document objects with page_content and metadata
        docs_with_scores = store.similarity_search_with_score(
            query=query_text,
            k=n_results,
            filter=where
        )
        
        # Format results to match the old ChromaDB interface
        formatted_documents = []
        formatted_metadatas = []
        formatted_distances = []
        
        for doc, score in docs_with_scores:
            formatted_documents.append(doc.page_content)
            formatted_metadatas.append(doc.metadata)
            formatted_distances.append(score)
            
        return {
            "documents": [formatted_documents],
            "metadatas": [formatted_metadatas],
            "distances": [formatted_distances]
        }
    
    def update_document(
        self,
        collection_name: str,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Update a document in a collection"""
        # Langchain PGVector doesn't have a direct update_document method in the older API.
        # We must delete and re-add.
        self.delete_documents(collection_name, [document_id])
        if document:
            self.add_documents(collection_name, [document], [metadata or {}], [document_id])
    
    def delete_documents(self, collection_name: str, ids: List[str]):
        """Delete documents from a collection"""
        store = self._get_store(collection_name)
        store.delete(ids=ids)
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get number of documents in a collection"""
        store = self._get_store(collection_name)
        # Using SQLAlchemy directly if we really need counts, but for now we can fall back to 0
        # or implement a raw query if absolutely needed.
        try:
            with store.session_maker() as session:
                from sqlalchemy import text
                stmt = text(f"SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = :name)")
                result = session.execute(stmt, {"name": collection_name}).scalar()
                return result or 0
        except Exception:
            return 0
    
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
            if results['documents'] and len(results['documents']) > 0:
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
            if results['documents'] and len(results['documents']) > 0:
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
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "insight": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i]
                    })
            return formatted_results
        except Exception:
            return []

# Singleton instance
vector_service = VectorDBService()
