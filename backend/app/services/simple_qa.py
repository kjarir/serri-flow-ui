import logging
import re
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Query, DocumentSection, ActivityLog

logger = logging.getLogger(__name__)


class SimpleQAService:
    """Simplified QA service that works without heavy ML dependencies"""
    
    def __init__(self):
        self.qa_pipeline = None
        self._load_qa_model()
    
    def _load_qa_model(self):
        """Load the Hugging Face QA pipeline or use fallback"""
        try:
            from transformers import pipeline
            self.qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-uncased-distilled-squad"
            )
            logger.info("Loaded QA model")
        except Exception as e:
            logger.warning(f"Could not load QA model: {e}")
            self.qa_pipeline = None
    
    def answer_question_simple(self, question: str, context: str) -> Tuple[str, float]:
        """Simple keyword-based answer extraction"""
        if not context.strip():
            return "I don't have enough information to answer this question.", 0.0
        
        # Convert to lowercase for matching
        question_lower = question.lower()
        context_lower = context.lower()
        
        # Extract key terms from question
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        # Find sentences that contain question words
        sentences = re.split(r'[.!?]+', context)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            # Calculate overlap
            overlap = len(question_words.intersection(sentence_words))
            if overlap > 0:
                relevant_sentences.append((sentence, overlap))
        
        if not relevant_sentences:
            return "I couldn't find relevant information in the document to answer your question.", 0.0
        
        # Sort by relevance and take the best sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        best_sentences = [sent for sent, _ in relevant_sentences[:2]]
        
        answer = " ".join(best_sentences).strip()
        confidence = min(0.8, len(relevant_sentences) * 0.2)  # Simple confidence score
        
        return answer, confidence
    
    def answer_question(self, question: str, context: str) -> Tuple[str, float]:
        """Answer a question given a context"""
        try:
            if self.qa_pipeline and context.strip():
                result = self.qa_pipeline(question=question, context=context)
                answer = result['answer']
                confidence = result['score']
                
                # If confidence is too low, use simple method
                if confidence < 0.1:
                    return self.answer_question_simple(question, context)
                
                return answer, confidence
            else:
                return self.answer_question_simple(question, context)
                
        except Exception as e:
            logger.error(f"Failed to answer question with model: {e}")
            return self.answer_question_simple(question, context)
    
    def generate_improved_answer(self, original_answer: str, feedback: str, context: str, question: str) -> str:
        """Generate an improved answer based on feedback"""
        try:
            if feedback == "not_helpful":
                return "I apologize that my previous answer wasn't helpful. Let me try a different approach. " + \
                       "Could you please provide more specific details about what you're looking for?"
            
            elif feedback == "too_vague":
                return "You're right, let me be more specific. " + \
                       f"Based on the document, {original_answer}. " + \
                       "Would you like me to elaborate on any particular aspect?"
            
            elif feedback == "good":
                return original_answer + " Is there anything else you'd like to know about this topic?"
            
            else:
                return original_answer
                
        except Exception as e:
            logger.error(f"Failed to generate improved answer: {e}")
            return original_answer
    
    def process_query(self, db: Session, document_id: int, question: str, document_processor) -> Query:
        """Process a query and return the answer"""
        try:
            # Find relevant sections
            relevant_sections = document_processor.find_relevant_sections(db, document_id, question)
            
            if not relevant_sections:
                # No relevant sections found
                query = Query(
                    document_id=document_id,
                    question=question,
                    answer="I couldn't find relevant information in the document to answer your question.",
                    confidence_score=0.0
                )
                db.add(query)
                db.commit()
                
                # Log the activity
                self._log_activity(db, "query_asked", "query", query.id, {
                    "question": question,
                    "document_id": document_id,
                    "relevant_sections_found": 0
                })
                
                return query
            
            # Combine relevant sections into context
            context = "\n\n".join([section.section_text for section in relevant_sections])
            
            # Get answer from QA pipeline
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
            
            # Log the activity
            self._log_activity(db, "query_asked", "query", query.id, {
                "question": question,
                "document_id": document_id,
                "relevant_sections_found": len(relevant_sections),
                "confidence_score": confidence
            })
            
            logger.info(f"Processed query {query.id} with confidence {confidence}")
            return query
            
        except Exception as e:
            logger.error(f"Failed to process query: {e}")
            raise
    
    def handle_feedback(self, db: Session, query_id: int, feedback: str) -> Query:
        """Handle feedback on a query and potentially improve the answer"""
        try:
            query = db.query(Query).filter(Query.id == query_id).first()
            if not query:
                raise ValueError(f"Query {query_id} not found")
            
            # Update feedback
            query.feedback = feedback
            query.iteration_count += 1
            
            # Generate improved answer if needed
            if feedback in ["not_helpful", "too_vague"]:
                # Get document sections for context
                sections = db.query(DocumentSection).filter(
                    DocumentSection.document_id == query.document_id
                ).all()
                
                if sections:
                    context = "\n\n".join([section.section_text for section in sections])
                    improved_answer = self.generate_improved_answer(
                        query.answer, feedback, context, query.question
                    )
                    query.answer = improved_answer
            
            db.commit()
            
            # Log the activity
            self._log_activity(db, "feedback_given", "query", query_id, {
                "feedback": feedback,
                "iteration_count": query.iteration_count
            })
            
            logger.info(f"Handled feedback for query {query_id}: {feedback}")
            return query
            
        except Exception as e:
            logger.error(f"Failed to handle feedback: {e}")
            raise
    
    def _log_activity(self, db: Session, action: str, entity_type: str, entity_id: int, details: dict = None):
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
