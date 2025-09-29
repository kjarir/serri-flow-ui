"""
ML-based Document Processor using PyMuPDF and scikit-learn
"""

import os
import re
import fitz  # PyMuPDF
import numpy as np
from typing import List, Tuple, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from app.models import Document, DocumentSection
import logging

logger = logging.getLogger(__name__)

class MLDocumentProcessor:
    """ML-based document processor with PyMuPDF and scikit-learn"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.document_vectors = {}
        self.section_texts = {}
        
    def process_document(self, file_path: str, db: Session) -> int:
        """Process document using PyMuPDF and create ML-ready chunks"""
        try:
            filename = os.path.basename(file_path)
            file_extension = filename.split(".").pop().lower()
            
            # Extract text using PyMuPDF
            if file_extension == "pdf":
                text_content = self._extract_text_with_pymupdf(file_path)
            elif file_extension == "txt":
                with open(file_path, "r", encoding="utf-8") as f:
                    text_content = f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Create document entry
            new_document = Document(
                filename=filename,
                file_path=file_path,
                file_type=file_extension.upper(),
                content="",  # Will be filled with processed content
                processed=True
            )
            db.add(new_document)
            db.commit()
            db.refresh(new_document)
            
            # Create intelligent chunks
            chunks = self._create_intelligent_chunks(text_content)
            
            # Store chunks in database
            chunk_texts = []
            for i, chunk_text in enumerate(chunks):
                if chunk_text.strip():
                    doc_section = DocumentSection(
                        document_id=new_document.id,
                        section_text=chunk_text.strip(),
                        section_index=i + 1,
                        embedding=[]  # Will be filled by ML model
                    )
                    db.add(doc_section)
                    chunk_texts.append(chunk_text.strip())
            
            db.commit()
            
            # Train ML model on this document
            self._train_ml_model(new_document.id, chunk_texts, db)
            
            logger.info(f"Successfully processed document {new_document.id} with {len(chunks)} chunks using ML")
            return new_document.id
            
        except Exception as e:
            logger.error(f"Error processing document: {e}", exc_info=True)
            raise
    
    def _extract_text_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text from PDF using PyMuPDF with better formatting"""
        try:
            doc = fitz.open(pdf_path)
            text_content = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                
                # Get text with formatting information
                text_dict = page.get_text("dict")
                
                # Extract text blocks in order
                for block in text_dict["blocks"]:
                    if "lines" in block:  # Text block
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                line_text += span["text"]
                            if line_text.strip():
                                text_content += line_text + "\n"
                
                # Add page break
                text_content += "\n--- PAGE BREAK ---\n"
            
            doc.close()
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {e}")
            # Fallback to simple text extraction
            doc = fitz.open(pdf_path)
            text_content = ""
            for page in doc:
                text_content += page.get_text()
            doc.close()
            return text_content
    
    def _create_intelligent_chunks(self, text: str) -> List[str]:
        """Create intelligent chunks based on content structure"""
        # Clean the text
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'--- PAGE BREAK ---', '\n\n', text)
        
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        max_chunk_size = 500  # words
        min_chunk_size = 50   # words
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max size, save current chunk
            if len(current_chunk.split()) + len(paragraph.split()) > max_chunk_size:
                if len(current_chunk.split()) >= min_chunk_size:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk.strip() and len(current_chunk.split()) >= min_chunk_size:
            chunks.append(current_chunk.strip())
        
        # If no chunks meet minimum size, create smaller chunks
        if not chunks:
            sentences = re.split(r'[.!?]+', text)
            current_chunk = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    if len(current_chunk.split()) + len(sentence.split()) > 200:
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                    else:
                        if current_chunk:
                            current_chunk += ". " + sentence
                        else:
                            current_chunk = sentence
            
            if current_chunk.strip():
                chunks.append(current_chunk.strip())
        
        return chunks
    
    def _train_ml_model(self, document_id: int, chunk_texts: List[str], db: Session):
        """Train ML model on document chunks"""
        try:
            if not chunk_texts:
                return
            
            # Fit TF-IDF vectorizer on chunks
            tfidf_matrix = self.vectorizer.fit_transform(chunk_texts)
            
            # Store vectors and texts for this document
            self.document_vectors[document_id] = tfidf_matrix
            self.section_texts[document_id] = chunk_texts
            
            # Update embeddings in database (store as serialized vectors)
            sections = db.query(DocumentSection).filter(
                DocumentSection.document_id == document_id
            ).all()
            
            for i, section in enumerate(sections):
                if i < len(chunk_texts):
                    # Store TF-IDF vector as embedding
                    vector = tfidf_matrix[i].toarray()[0]
                    section.embedding = vector.tolist()
                    db.add(section)
            
            db.commit()
            logger.info(f"Trained ML model for document {document_id} with {len(chunk_texts)} chunks")
            
        except Exception as e:
            logger.error(f"Error training ML model: {e}", exc_info=True)
    
    def find_relevant_sections(self, db: Session, document_id: int, question: str, top_k: int = 3) -> List[DocumentSection]:
        """Find relevant sections using ML similarity"""
        try:
            if document_id not in self.document_vectors:
                # Fallback to simple keyword matching
                return self._fallback_keyword_search(db, document_id, question)
            
            # Get TF-IDF matrix for this document
            tfidf_matrix = self.document_vectors[document_id]
            chunk_texts = self.section_texts[document_id]
            
            # Transform question using same vectorizer
            question_vector = self.vectorizer.transform([question])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(question_vector, tfidf_matrix).flatten()
            
            # Get top-k most similar chunks
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Get sections from database
            sections = db.query(DocumentSection).filter(
                DocumentSection.document_id == document_id
            ).all()
            
            relevant_sections = []
            for idx in top_indices:
                if idx < len(sections) and similarities[idx] > 0.1:  # Minimum similarity threshold
                    relevant_sections.append(sections[idx])
            
            logger.info(f"Found {len(relevant_sections)} relevant sections for document {document_id}")
            return relevant_sections
            
        except Exception as e:
            logger.error(f"Error finding relevant sections: {e}", exc_info=True)
            return self._fallback_keyword_search(db, document_id, question)
    
    def _fallback_keyword_search(self, db: Session, document_id: int, question: str) -> List[DocumentSection]:
        """Fallback keyword search if ML fails"""
        try:
            # Simple keyword matching
            question_words = set(re.findall(r'\b\w+\b', question.lower()))
            stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'when', 'where', 'why', 'who', 'which', 'can', 'could', 'would', 'should', 'may', 'might', 'will', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'been', 'being', 'was', 'were'}
            question_words = question_words - stop_words
            
            sections = db.query(DocumentSection).filter(
                DocumentSection.document_id == document_id
            ).all()
            
            scored_sections = []
            for section in sections:
                section_words = set(re.findall(r'\b\w+\b', section.section_text.lower()))
                overlap = len(question_words.intersection(section_words))
                if overlap > 0:
                    scored_sections.append((section, overlap))
            
            # Sort by overlap score
            scored_sections.sort(key=lambda x: x[1], reverse=True)
            
            return [section for section, score in scored_sections[:3]]
            
        except Exception as e:
            logger.error(f"Error in fallback search: {e}", exc_info=True)
            return []
