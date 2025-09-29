"""
Universal ML-based QA that handles ANY question properly
"""

import re
import numpy as np
from typing import Tuple, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from app.models import Document, DocumentSection, Query
import logging

logger = logging.getLogger(__name__)

class UniversalMLQA:
    """Universal ML QA that handles ANY question properly"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=3000,
            stop_words='english',
            ngram_range=(1, 3),
            lowercase=True,
            min_df=1,
            max_df=0.9
        )
    
    def answer_question(self, question: str, context: str) -> Tuple[str, float]:
        """Handle ANY question using universal ML approach"""
        if not context.strip():
            return "I don't have enough information to answer this question.", 0.0
        
        # Step 1: Clean and preprocess context
        cleaned_context = self._preprocess_context(context)
        
        # Step 2: Use universal ML to find relevant content
        relevant_content = self._universal_ml_search(question, cleaned_context)
        
        # Step 3: Generate proper answer from relevant content
        answer, confidence = self._generate_universal_answer(question, relevant_content)
        
        return answer, confidence
    
    def _preprocess_context(self, context: str) -> str:
        """Clean context for better ML analysis"""
        # Remove extra whitespace
        context = re.sub(r'\s+', ' ', context)
        
        # Remove common PDF artifacts
        context = re.sub(r'This page intentionally left blank', '', context, flags=re.IGNORECASE)
        context = re.sub(r'--- PAGE BREAK ---', '', context)
        context = re.sub(r'^\d+\s*$', '', context, flags=re.MULTILINE)
        
        return context.strip()
    
    def _universal_ml_search(self, question: str, context: str) -> str:
        """Universal ML search that works for ANY question"""
        try:
            # Split into sentences
            sentences = re.split(r'[.!?]+', context)
            sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
            
            if not sentences:
                return context[:500]
            
            # Extract key terms from question (universal approach)
            question_terms = self._extract_question_terms(question)
            
            # Create TF-IDF vectors
            all_texts = [question] + sentences
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate similarities
            question_vector = tfidf_matrix[0:1]
            sentence_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(question_vector, sentence_vectors).flatten()
            
            # Get relevant sentences with multiple criteria
            relevant_sentences = []
            
            for i, similarity in enumerate(similarities):
                sentence = sentences[i]
                
                # Check similarity score
                if similarity > 0.15:  # Lower threshold for more results
                    relevant_sentences.append((sentence, similarity, 'similarity'))
                
                # Check keyword overlap
                keyword_score = self._calculate_keyword_overlap(question_terms, sentence)
                if keyword_score > 0:
                    relevant_sentences.append((sentence, keyword_score, 'keywords'))
            
            # Remove duplicates and sort by score
            unique_sentences = {}
            for sentence, score, method in relevant_sentences:
                if sentence not in unique_sentences or score > unique_sentences[sentence][0]:
                    unique_sentences[sentence] = (score, method)
            
            # Sort by score
            sorted_sentences = sorted(unique_sentences.items(), key=lambda x: x[1][0], reverse=True)
            
            if sorted_sentences:
                # Take top 2-3 most relevant sentences
                top_sentences = [sent for sent, (score, method) in sorted_sentences[:3]]
                return ' '.join(top_sentences)
            else:
                # Fallback: return first meaningful sentences
                return ' '.join(sentences[:3])
                
        except Exception as e:
            logger.error(f"Universal ML search error: {e}")
            return self._fallback_search(question, context)
    
    def _extract_question_terms(self, question: str) -> set:
        """Extract key terms from ANY question"""
        # Get all words
        words = set(re.findall(r'\b\w+\b', question.lower()))
        
        # Remove common stop words
        stop_words = {
            'what', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 
            'how', 'when', 'where', 'why', 'who', 'which', 'can', 'could', 'would', 'should', 'may', 'might', 'will', 
            'do', 'does', 'did', 'have', 'has', 'had', 'be', 'been', 'being', 'was', 'were', 'tell', 'me', 'about', 
            'something', 'explain', 'describe', 'define', 'give', 'show', 'list', 'name', 'find', 'get', 'know'
        }
        
        return words - stop_words
    
    def _calculate_keyword_overlap(self, question_terms: set, sentence: str) -> float:
        """Calculate keyword overlap score"""
        sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
        overlap = len(question_terms.intersection(sentence_words))
        return overlap / len(question_terms) if question_terms else 0
    
    def _fallback_search(self, question: str, context: str) -> str:
        """Fallback search when ML fails"""
        question_terms = self._extract_question_terms(question)
        sentences = context.split('.')
        
        best_sentence = ""
        max_score = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 15:
                continue
            
            score = self._calculate_keyword_overlap(question_terms, sentence)
            if score > max_score:
                max_score = score
                best_sentence = sentence
        
        return best_sentence if best_sentence else sentences[0] if sentences else ""
    
    def _generate_universal_answer(self, question: str, relevant_content: str) -> Tuple[str, float]:
        """Generate answer for ANY question type"""
        if not relevant_content.strip():
            return "I couldn't find relevant information to answer your question.", 0.3
        
        # Clean up the relevant content
        relevant_content = re.sub(r'\s+', ' ', relevant_content).strip()
        
        # If we have good content, use it directly
        if len(relevant_content) > 20:
            # Make sure it ends properly
            if not relevant_content.endswith('.'):
                relevant_content += '.'
            
            # Calculate confidence based on content quality
            confidence = min(0.9, len(relevant_content) / 200)  # Longer content = higher confidence
            
            return f"Based on the document: {relevant_content}", confidence
        
        return "I found some information but it's not complete enough to answer your question.", 0.4
    
    def process_query(self, db: Session, document_id: int, question: str, document_processor) -> Query:
        """Process ANY query with universal ML approach"""
        try:
            # Get document sections
            sections = db.query(DocumentSection).filter(
                DocumentSection.document_id == document_id
            ).all()
            
            if not sections:
                answer, confidence = "I couldn't find any content in this document.", 0.0
            else:
                # Combine all sections
                context = "\n".join([section.section_text for section in sections])
                
                # Use universal ML analysis
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
            
            logger.info(f"Processed universal ML query {query.id} with confidence {confidence}")
            return query
            
        except Exception as e:
            logger.error(f"Failed to process universal ML query: {e}", exc_info=True)
            raise
