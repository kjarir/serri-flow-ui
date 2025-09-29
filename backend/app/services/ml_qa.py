"""
ML-based QA Service using scikit-learn and advanced text processing
"""

import re
import numpy as np
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from app.models import Document, DocumentSection, Query, ActivityLog
import logging

logger = logging.getLogger(__name__)

class MLQAService:
    """ML-based QA service with advanced text processing"""
    
    def __init__(self):
        self.qa_vectorizer = TfidfVectorizer(
            max_features=500,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True
        )
        self.question_patterns = {}
        self.answer_templates = {}
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize question patterns and answer templates"""
        self.question_patterns = {
            'author': [r'author', r'writer', r'written by', r'who wrote'],
            'title': [r'title', r'name of.*book', r'what.*called'],
            'date': [r'date', r'when', r'time'],
            'harvest_date': [r'harvest.*date', r'harvested.*date'],
            'batch_id': [r'batch.*id', r'batch'],
            'farmer': [r'farmer', r'grower', r'who.*farmer'],
            'crop': [r'crop', r'rice', r'what.*type'],
            'quantity': [r'quantity', r'amount', r'how much', r'kg'],
            'group_id': [r'group.*id', r'group'],
            'group_name': [r'group.*name'],
            'grading': [r'grading', r'grade', r'quality'],
            'generated': [r'generated', r'created', r'when.*generated'],
            'rules': [r'rule', r'regulation', r'guideline'],
            'dress_code': [r'dress.*code', r'attire', r'clothing'],
            'time': [r'time', r'arrive', r'when.*arrive'],
            'overview': [r'about', r'overview', r'summary', r'content', r'tell.*about', r'explain', r'what.*about'],
            'pricing': [r'pricing', r'price', r'cost', r'plan', r'how much']
        }
        
        self.answer_templates = {
            'author': "The author is {value}.",
            'title': "The title is: {value}.",
            'date': "The date is {value}.",
            'harvest_date': "The harvest date is {value}.",
            'batch_id': "The batch ID is {value}.",
            'farmer': "The farmer is {value}.",
            'crop': "The crop is {value}.",
            'quantity': "The quantity is {value}.",
            'group_id': "The group ID is {value}.",
            'group_name': "The group name is {value}.",
            'grading': "The grading is {value}.",
            'generated': "The generated date is {value}.",
            'rules': "The rules are: {value}.",
            'dress_code': "The dress code is: {value}.",
            'time': "You should arrive {value}.",
            'overview': "This document appears to be about: {value}",
            'pricing': "The pricing information is: {value}"
        }
    
    def answer_question(self, question: str, context: str) -> Tuple[str, float]:
        """Answer question using ML-based approach"""
        try:
            if not context.strip():
                return "I don't have enough information to answer this question.", 0.0
            
            question_lower = question.lower().strip()
            
            # First, try pattern-based extraction
            pattern_answer = self._extract_by_patterns(question_lower, context)
            if pattern_answer[1] > 0.8:  # High confidence pattern match
                return pattern_answer
            
            # Then try ML-based similarity
            ml_answer = self._ml_similarity_answer(question, context)
            if ml_answer[1] > 0.6:  # Good ML match
                return ml_answer
            
            # Finally, provide general overview
            return self._provide_intelligent_overview(context, question_lower)
            
        except Exception as e:
            logger.error(f"Error in ML QA: {e}", exc_info=True)
            return "I encountered an error while processing your question.", 0.0
    
    def _extract_by_patterns(self, question: str, context: str) -> Tuple[str, float]:
        """Extract answer using predefined patterns"""
        for pattern_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    value = self._extract_value_by_type(pattern_type, context)
                    if value:
                        template = self.answer_templates.get(pattern_type, "The answer is {value}.")
                        return template.format(value=value), 0.9
        
        return "", 0.0
    
    def _extract_value_by_type(self, pattern_type: str, context: str) -> str:
        """Extract specific value based on pattern type"""
        extraction_patterns = {
            'author': [
                r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'author[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'written\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
                r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)'
            ],
            'title': [
                r'title[:\s]+([^.\n]+)',
                r'book[:\s]+([^.\n]+)'
            ],
            'harvest_date': [
                r'harvest\s+date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})',
                r'harvested\s+date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})'
            ],
            'batch_id': [
                r'batch\s+id[:\s]+([A-Za-z0-9\-]+)',
                r'batch[:\s]+([A-Za-z0-9\-]+)'
            ],
            'farmer': [
                r'farmer[:\s]+([A-Za-z\s]+?)(?:\s+Crop|$)',
                r'grower[:\s]+([A-Za-z\s]+?)(?:\s+Crop|$)'
            ],
            'crop': [
                r'crop[:\s]+([A-Za-z\s\-]+?)(?:\s+Quantity|$)',
                r'rice[:\s]+([A-Za-z\s\-]+)'
            ],
            'quantity': [
                r'quantity[:\s]+([0-9]+\s*[A-Za-z]+)',
                r'([0-9]+\s*kg)'
            ],
            'group_id': [
                r'group\s+id[:\s]+([A-Za-z0-9\-]+)',
                r'group[:\s]+([A-Za-z0-9\-]+)'
            ],
            'group_name': [
                r'group\s+name[:\s]+([A-Za-z0-9_\-]+)'
            ],
            'grading': [
                r'grading[:\s]+([A-Za-z]+)',
                r'grade[:\s]+([A-Za-z]+)'
            ],
            'generated': [
                r'generated[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})',
                r'generated[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})'
            ],
            'time': [
                r'([0-9]+\s*minutes?\s*before)',
                r'([0-9]+:[0-9]+\s*[AP]M)',
                r'(at least\s+[0-9]+\s*minutes?)'
            ],
            'dress_code': [
                r'(formal\s+attire)',
                r'(decent\s+and\s+sober)',
                r'(dress\s+code)'
            ],
            'pricing': [
                r'pricing[:\s]+([^.\n]+)',
                r'price[:\s]+([^.\n]+)',
                r'plan[:\s]+([^.\n]+)',
                r'(\$[0-9]+/[a-z]+)',
                r'([0-9]+\s*[a-z]+\s*plan)'
            ]
        }
        
        patterns = extraction_patterns.get(pattern_type, [])
        for pattern in patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                value = matches[0].strip()
                # Clean up the value
                value = re.sub(r'\s+', ' ', value)
                if len(value) > 1 and len(value) < 100:
                    return value
        
        return ""
    
    def _ml_similarity_answer(self, question: str, context: str) -> Tuple[str, float]:
        """Answer using ML similarity matching"""
        try:
            # Split context into sentences
            sentences = re.split(r'[.!?]+', context)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
            
            if not sentences:
                return "", 0.0
            
            # Create TF-IDF vectors
            all_texts = [question] + sentences
            tfidf_matrix = self.qa_vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            question_vector = tfidf_matrix[0:1]
            sentence_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(question_vector, sentence_vectors).flatten()
            
            # Get best matching sentence
            best_idx = np.argmax(similarities)
            best_similarity = similarities[best_idx]
            
            if best_similarity > 0.3:  # Minimum similarity threshold
                best_sentence = sentences[best_idx]
                return best_sentence, float(best_similarity)
            
            return "", 0.0
            
        except Exception as e:
            logger.error(f"Error in ML similarity: {e}", exc_info=True)
            return "", 0.0
    
    def _provide_intelligent_overview(self, context: str, question: str) -> Tuple[str, float]:
        """Provide intelligent overview based on question type"""
        try:
            # For general questions, provide document overview
            if any(word in question for word in ['about', 'what', 'overview', 'summary', 'content', 'tell', 'explain', 'say', 'give']):
                # Get the first few meaningful sentences
                sentences = re.split(r'[.!?]+', context)
                sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 20]
                
                if sentences:
                    # Take the first 2-3 meaningful sentences
                    overview_sentences = sentences[:3]
                    overview = " ".join(overview_sentences).strip()
                    
                    # Clean up the overview
                    overview = re.sub(r'\s+', ' ', overview)
                    if not overview.endswith('.'):
                        overview += '.'
                    
                    return f"This document appears to be about: {overview}", 0.7
            
            # For other questions, try to find relevant information
            lines = context.split('\n')
            for line in lines:
                line = line.strip()
                if len(line) > 20 and any(word in line.lower() for word in question.split()):
                    return f"Based on the document content: {line}", 0.6
            
            # Last resort: provide first meaningful line
            for line in lines:
                line = line.strip()
                if len(line) > 30:
                    return f"This document contains: {line}", 0.5
            
            return "I found content in the document but couldn't determine a specific answer to your question.", 0.3
            
        except Exception as e:
            logger.error(f"Error in intelligent overview: {e}", exc_info=True)
            return "I encountered an error while processing your question.", 0.0
    
    def process_query(self, db: Session, document_id: int, question: str, document_processor) -> Query:
        """Process query using ML-based approach"""
        try:
            # Get document info for filename-based answers
            from app.models import Document, DocumentSection
            document = db.query(Document).filter(Document.id == document_id).first()
            
            # Check if we can answer from filename first
            question_lower = question.lower()
            if 'author' in question_lower or 'writer' in question_lower:
                filename_answer = self._extract_author_from_filename(document.filename if document else "")
                if filename_answer:
                    query = Query(
                        document_id=document_id,
                        question=question,
                        answer=filename_answer,
                        confidence_score=0.95
                    )
                    db.add(query)
                    db.commit()
                    return query
            
            # Find relevant sections using ML
            relevant_sections = document_processor.find_relevant_sections(db, document_id, question)
            
            if not relevant_sections:
                # Get all sections for general overview
                all_sections = db.query(DocumentSection).filter(DocumentSection.document_id == document_id).all()
                if all_sections:
                    all_content = "\n\n".join([section.section_text for section in all_sections])
                    general_answer, confidence = self._provide_intelligent_overview(all_content, question_lower)
                else:
                    general_answer, confidence = "I found the document but couldn't extract any readable content from it.", 0.3
                
                query = Query(
                    document_id=document_id,
                    question=question,
                    answer=general_answer,
                    confidence_score=confidence
                )
                db.add(query)
                db.commit()
                return query
            
            # Combine relevant sections
            context = "\n\n".join([section.section_text for section in relevant_sections])
            
            # Get ML-based answer
            answer, confidence = self.answer_question(question, context)
            
            # Create query record
            query = Query(
                document_id=document_id,
                question=question,
                answer=answer,
                confidence_score=confidence
            )
            db.add(query)
            db.commit()
            
            logger.info(f"Processed ML query {query.id} with confidence {confidence}")
            return query
            
        except Exception as e:
            logger.error(f"Failed to process ML query: {e}", exc_info=True)
            raise
    
    def _extract_author_from_filename(self, filename: str) -> str:
        """Extract author name from filename"""
        if not filename:
            return ""
        
        name_without_ext = filename.replace('.pdf', '').replace('.txt', '').replace('.docx', '')
        parts = re.split(r'\s*-\s*|\s*_\s*|\s*by\s*', name_without_ext)
        
        if len(parts) >= 2:
            author_part = parts[0].strip()
            author_part = re.sub(r'\s+', ' ', author_part)
            words = author_part.split()
            if len(words) >= 2 and all(word[0].isupper() for word in words if word):
                return f"The author is {author_part}."
        
        return ""
