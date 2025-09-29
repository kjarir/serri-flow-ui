import os
import logging
import re
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from sqlalchemy.orm import Session
from app.models import Document, DocumentSection, ActivityLog

logger = logging.getLogger(__name__)


class FastDocumentProcessor:
    """Ultra-fast document processor using simple text processing"""
    
    def __init__(self):
        pass  # No heavy model loading
    
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
    
    def split_text_into_sections(self, text: str, max_section_length: int = 800) -> List[str]:
        """Split text into manageable sections for better processing"""
        # Split by paragraphs, sentences, or fixed length
        sections = []
        
        # First try splitting by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            if len(paragraph) <= max_section_length:
                sections.append(paragraph)
            else:
                # Split long paragraphs by sentences
                sentences = re.split(r'[.!?]+', paragraph)
                current_section = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    
                    if len(current_section) + len(sentence) <= max_section_length:
                        if current_section:
                            current_section += ". " + sentence
                        else:
                            current_section = sentence
                    else:
                        if current_section:
                            sections.append(current_section)
                        current_section = sentence
                
                if current_section:
                    sections.append(current_section)
        
        return sections
    
    def process_document(self, db: Session, document: Document) -> bool:
        """Process a document: extract text and split into sections"""
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
            
            # Save sections to database (no embeddings for speed)
            for i, section_text in enumerate(sections):
                section = DocumentSection(
                    document_id=document.id,
                    section_text=section_text,
                    section_index=i,
                    embedding=None  # No embeddings for speed
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
        """Find the most relevant sections using fast keyword matching"""
        try:
            # Get all sections for the document
            sections = db.query(DocumentSection).filter(
                DocumentSection.document_id == document_id
            ).all()
            
            if not sections:
                return []
            
            # Simple keyword-based scoring
            query_words = set(re.findall(r'\b\w+\b', query.lower()))
            scored_sections = []
            
            for section in sections:
                section_words = set(re.findall(r'\b\w+\b', section.section_text.lower()))
                
                # Calculate overlap score
                overlap = len(query_words.intersection(section_words))
                if overlap > 0:
                    # Bonus for exact phrase matches
                    if query.lower() in section.section_text.lower():
                        overlap += 5
                    
                    scored_sections.append((section, overlap))
            
            # Sort by score and return top_k
            scored_sections.sort(key=lambda x: x[1], reverse=True)
            return [section for section, _ in scored_sections[:top_k]]
            
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
