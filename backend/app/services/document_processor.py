import os
import logging
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
from sqlalchemy.orm import Session
from app.models import Document, DocumentSection, ActivityLog
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        self.embedding_model = None
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        """Load the sentence transformer model for embeddings"""
        try:
            self.embedding_model = SentenceTransformer(settings.embedding_model)
            logger.info(f"Loaded embedding model: {settings.embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {file_path}: {e}")
            raise
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Failed to extract text from TXT {file_path}: {e}")
            raise
    
    def split_text_into_sections(self, text: str, max_section_length: int = 500) -> List[str]:
        """Split text into manageable sections for better processing"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        sections = []
        current_section = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # If adding this paragraph would exceed max length, save current section
            if len(current_section) + len(paragraph) > max_section_length and current_section:
                sections.append(current_section.strip())
                current_section = paragraph
            else:
                if current_section:
                    current_section += "\n\n" + paragraph
                else:
                    current_section = paragraph
        
        # Add the last section if it exists
        if current_section:
            sections.append(current_section.strip())
        
        return sections
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_tensor=False)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            raise
    
    def process_document(self, db: Session, document: Document) -> bool:
        """Process a document: extract text, split into sections, create embeddings"""
        try:
            # Extract text based on file type
            if document.file_type.lower() == 'pdf':
                content = self.extract_text_from_pdf(document.file_path)
            elif document.file_type.lower() == 'txt':
                content = self.extract_text_from_txt(document.file_path)
            else:
                raise ValueError(f"Unsupported file type: {document.file_type}")
            
            # Update document content
            document.content = content
            
            # Split text into sections
            sections = self.split_text_into_sections(content)
            
            # Create embeddings for all sections
            embeddings = self.create_embeddings(sections)
            
            # Save sections to database
            for i, (section_text, embedding) in enumerate(zip(sections, embeddings)):
                section = DocumentSection(
                    document_id=document.id,
                    section_text=section_text,
                    section_index=i,
                    embedding=embedding
                )
                db.add(section)
            
            # Mark document as processed
            document.processed = True
            db.commit()
            
            # Log the activity
            self._log_activity(db, "document_processed", "document", document.id, {
                "filename": document.filename,
                "sections_count": len(sections),
                "file_type": document.file_type
            })
            
            logger.info(f"Successfully processed document {document.id} with {len(sections)} sections")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process document {document.id}: {e}")
            db.rollback()
            return False
    
    def find_relevant_sections(self, db: Session, document_id: int, query: str, top_k: int = 3) -> List[DocumentSection]:
        """Find the most relevant sections for a query using semantic search"""
        try:
            # Get all sections for the document
            sections = db.query(DocumentSection).filter(
                DocumentSection.document_id == document_id
            ).all()
            
            if not sections:
                return []
            
            # Create embedding for the query
            query_embedding = self.embedding_model.encode([query], convert_to_tensor=False)[0]
            
            # Calculate similarities
            similarities = []
            for section in sections:
                if section.embedding:
                    # Calculate cosine similarity
                    similarity = np.dot(query_embedding, section.embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(section.embedding)
                    )
                    similarities.append((section, similarity))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return [section for section, _ in similarities[:top_k]]
            
        except Exception as e:
            logger.error(f"Failed to find relevant sections: {e}")
            return []
    
    def _log_activity(self, db: Session, action: str, entity_type: str, entity_id: int, details: Dict[str, Any] = None):
        """Log an activity to the database"""
        try:
            log_entry = ActivityLog(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
