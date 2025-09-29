import logging
from typing import List, Optional, Tuple
from transformers import pipeline
from sqlalchemy.orm import Session
from app.models import Query, DocumentSection, ActivityLog
from app.config import settings

logger = logging.getLogger(__name__)


class QAService:
    def __init__(self):
        self.qa_pipeline = None
        self._load_qa_model()
    
    def _load_qa_model(self):
        """Load the Hugging Face QA pipeline"""
        try:
            self.qa_pipeline = pipeline(
                "question-answering",
                model=settings.qa_model,
                tokenizer=settings.qa_model
            )
            logger.info(f"Loaded QA model: {settings.qa_model}")
        except Exception as e:
            logger.error(f"Failed to load QA model: {e}")
            raise
    
    def answer_question(self, question: str, context: str) -> Tuple[str, float]:
        """Answer a question given a context using the QA pipeline"""
        try:
            if not context.strip():
                return "I don't have enough information to answer this question.", 0.0
            
            result = self.qa_pipeline(question=question, context=context)
            answer = result['answer']
            confidence = result['score']
            
            # If confidence is too low, provide a fallback response
            if confidence < 0.1:
                return "I'm not confident about this answer. Could you please rephrase your question or provide more context?", confidence
            
            return answer, confidence
            
        except Exception as e:
            logger.error(f"Failed to answer question: {e}")
            return "I encountered an error while processing your question. Please try again.", 0.0
    
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
