import logging
import re
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Query, DocumentSection, ActivityLog

logger = logging.getLogger(__name__)


class FastQAService:
    """Ultra-fast QA service using simple text processing"""
    
    def __init__(self):
        pass  # No heavy model loading
    
    def answer_question(self, question: str, context: str) -> Tuple[str, float]:
        """Improved keyword-based answer extraction with better relevance"""
        if not context.strip():
            return "I don't have enough information to answer this question.", 0.0
        
        # Convert to lowercase for matching
        question_lower = question.lower().strip()
        context_lower = context.lower()
        
        # Handle specific question types
        if 'author' in question_lower or 'writer' in question_lower or 'written by' in question_lower:
            return self._find_author_info(context)
        elif 'title' in question_lower or 'name of the book' in question_lower:
            return self._find_title_info(context)
        elif 'harvest' in question_lower and 'date' in question_lower:
            return self._find_harvest_date(context)
        elif 'date' in question_lower:
            return self._find_date_info(context, question_lower)
        elif 'chapter' in question_lower:
            return self._find_chapter_info(context, question_lower)
        elif 'page' in question_lower:
            return self._find_page_info(context, question_lower)
        elif 'batch' in question_lower and 'id' in question_lower:
            return self._find_batch_id(context)
        elif 'farmer' in question_lower or 'grower' in question_lower:
            return self._find_farmer_info(context)
        elif 'crop' in question_lower:
            return self._find_crop_info(context)
        elif 'quantity' in question_lower:
            return self._find_quantity_info(context)
        elif 'group' in question_lower and 'id' in question_lower:
            return self._find_group_id(context)
        elif 'group' in question_lower and 'name' in question_lower:
            return self._find_group_name(context)
        elif 'grading' in question_lower or 'grade' in question_lower:
            return self._find_grading_info(context)
        elif 'generated' in question_lower:
            return self._find_generated_date(context)
        
        # Extract key terms from question
        question_words = set(re.findall(r'\b\w+\b', question_lower))
        
        # Remove common stop words
        stop_words = {'what', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'when', 'where', 'why', 'who', 'which', 'can', 'could', 'would', 'should', 'may', 'might', 'will', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'been', 'being', 'was', 'were', 'name', 'of', 'the', 'this', 'that', 'these', 'those'}
        question_words = question_words - stop_words
        
        # Find sentences that contain question words
        sentences = re.split(r'[.!?]+', context)
        relevant_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence or len(sentence) < 10:  # Skip very short sentences
                continue
            
            sentence_words = set(re.findall(r'\b\w+\b', sentence.lower()))
            sentence_words = sentence_words - stop_words
            
            # Calculate overlap
            overlap = len(question_words.intersection(sentence_words))
            if overlap > 0:
                # Bonus for exact phrase matches
                if any(word in sentence.lower() for word in question_words):
                    overlap += 3
                
                # Bonus for longer, more informative sentences
                if len(sentence) > 50:
                    overlap += 1
                
                relevant_sentences.append((sentence, overlap))
        
        if not relevant_sentences:
            # If no specific matches, try to provide a general overview from the document
            return self._provide_general_overview(context, question_lower)
        
        # If we have relevant sentences but they're not good enough, also try general overview
        if relevant_sentences and relevant_sentences[0][1] < 2:  # Low relevance score
            general_answer = self._provide_general_overview(context, question_lower)
            if general_answer[1] > 0.5:  # If general overview is better
                return general_answer
        
        # Sort by relevance and take the best sentences
        relevant_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # For general questions, try to extract the most relevant information
        best_sentence = relevant_sentences[0][0]
        
        # Try to extract specific information based on question keywords
        extracted_info = self._extract_specific_info(best_sentence, question_lower)
        if extracted_info:
            return extracted_info, 0.9
        
        # If no specific extraction, return the best sentence
        answer = re.sub(r'\s+', ' ', best_sentence).strip()
        if not answer.endswith('.'):
            answer += '.'
        
        # Calculate confidence based on overlap
        confidence = min(0.9, relevant_sentences[0][1] * 0.2)
        
        return answer, confidence
    
    def _extract_specific_info(self, text: str, question: str) -> str:
        """Extract specific information from text based on question keywords"""
        text_lower = text.lower()
        
        # Look for specific patterns based on question keywords
        if 'id' in question:
            # Look for ID patterns
            id_patterns = [
                r'([A-Za-z0-9\-]{8,})',  # UUID-like patterns
                r'id[:\s]+([A-Za-z0-9\-]+)',
            ]
            for pattern in id_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return f"The ID is {matches[0]}."
        
        if 'name' in question:
            # Look for name patterns
            name_patterns = [
                r'name[:\s]+([A-Za-z0-9_\-]+)',
            ]
            for pattern in name_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return f"The name is {matches[0]}."
        
        if 'date' in question:
            # Look for date patterns
            date_patterns = [
                r'([0-9]{4}-[0-9]{2}-[0-9]{2})',
                r'([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            ]
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return f"The date is {matches[0]}."
        
        if 'amount' in question or 'quantity' in question or 'kg' in question or 'how much' in question:
            # Look for quantity patterns
            quantity_patterns = [
                r'quantity[:\s]+([0-9]+\s*[A-Za-z]+)',
                r'([0-9]+\s*kg)',
            ]
            for pattern in quantity_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return f"The quantity is {matches[0]}."
        
        if 'type' in question or 'kind' in question or 'rice' in question:
            # Look for crop/rice type patterns
            crop_patterns = [
                r'crop[:\s]+([A-Za-z\s\-]+?)(?:\s+Quantity|$)',
                r'rice[:\s]+([A-Za-z\s\-]+)',
            ]
            for pattern in crop_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    crop = matches[0].strip()
                    crop = re.sub(r'\s+Quantity$', '', crop).strip()
                    if len(crop) > 2:
                        return f"The rice type is {crop}."
        
        if 'time' in question or 'arrive' in question or 'when' in question:
            # Look for time-related patterns
            time_patterns = [
                r'([0-9]+\s*minutes?\s*before)',
                r'([0-9]+:[0-9]+\s*[AP]M)',
                r'(at least\s+[0-9]+\s*minutes?)',
            ]
            for pattern in time_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return f"You should arrive {matches[0]}."
        
        if 'dress' in question or 'attire' in question or 'clothing' in question:
            # Look for dress code patterns
            dress_patterns = [
                r'(formal\s+attire)',
                r'(decent\s+and\s+sober)',
                r'(dress\s+code)',
            ]
            for pattern in dress_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    return f"The dress code is: {matches[0]}."
        
        return None
    
    def _provide_general_overview(self, context: str, question: str) -> Tuple[str, float]:
        """Provide a general overview when no specific matches are found"""
        if not context.strip():
            return "I couldn't find any content in this document to answer your question.", 0.0
        
        # For general questions like "what is this about", provide document overview
        if any(word in question for word in ['about', 'what', 'overview', 'summary', 'content', 'tell', 'explain', 'say', 'give']):
            # Get the first few sentences or lines as an overview
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
        
        # For other questions, try to find any relevant information
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
    
    def _find_author_info(self, context: str) -> Tuple[str, float]:
        """Find author information in the document"""
        # Look for common author patterns
        author_patterns = [
            r'by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'author[:\s]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'written\s+by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)',  # First M. Last format
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                author = matches[0].strip()
                if len(author) > 3 and len(author) < 50:  # Reasonable author name length
                    return f"The author is {author}.", 0.9
        
        # If no clear author pattern, look for names in the first few lines
        lines = context.split('\n')[:10]  # Check first 10 lines
        for line in lines:
            # Look for capitalized names
            names = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', line)
            if names:
                return f"The author appears to be {names[0]}.", 0.7
        
        return "I couldn't find the author information in this document.", 0.0
    
    def _find_title_info(self, context: str) -> Tuple[str, float]:
        """Find title information in the document"""
        # Look for title patterns
        title_patterns = [
            r'title[:\s]+([^.\n]+)',
            r'book[:\s]+([^.\n]+)',
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                title = matches[0].strip()
                if len(title) > 5:
                    return f"The title is: {title}.", 0.9
        
        # Look in the first line for potential title
        first_line = context.split('\n')[0].strip()
        if len(first_line) > 10 and len(first_line) < 100:
            return f"The title appears to be: {first_line}.", 0.7
        
        return "I couldn't find the title information in this document.", 0.0
    
    def _find_chapter_info(self, context: str, question: str) -> Tuple[str, float]:
        """Find chapter information"""
        # Look for chapter patterns
        chapter_patterns = [
            r'chapter\s+(\d+)',
            r'chapter\s+([ivxlcdm]+)',
        ]
        
        for pattern in chapter_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                chapter = matches[0]
                return f"Chapter {chapter} is mentioned in the document.", 0.8
        
        return "I couldn't find specific chapter information.", 0.0
    
    def _find_page_info(self, context: str, question: str) -> Tuple[str, float]:
        """Find page information"""
        # Look for page patterns
        page_patterns = [
            r'page\s+(\d+)',
            r'p\.\s*(\d+)',
        ]
        
        for pattern in page_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                page = matches[0]
                return f"Page {page} is referenced in the document.", 0.8
        
        return "I couldn't find specific page information.", 0.0
    
    def _find_harvest_date(self, context: str) -> Tuple[str, float]:
        """Find harvest date from certificate"""
        # Look for harvest date patterns
        harvest_patterns = [
            r'harvest\s+date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'harvested\s+date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'harvest\s+date[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'harvest\s+date[:\s]+([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})',
        ]
        
        for pattern in harvest_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                date = matches[0].strip()
                return f"The harvest date is {date}.", 0.95
        
        # Look for any date pattern near "harvest"
        lines = context.split('\n')
        for line in lines:
            if 'harvest' in line.lower() and any(char.isdigit() for char in line):
                # Extract date from the line
                date_match = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2})', line)
                if date_match:
                    return f"The harvest date is {date_match.group(1)}.", 0.9
        
        return "I couldn't find the harvest date in this document.", 0.0
    
    def _find_date_info(self, context: str, question: str) -> Tuple[str, float]:
        """Find general date information"""
        # Look for various date patterns
        date_patterns = [
            r'date[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})',
            r'date[:\s]+([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})',
            r'date[:\s]+([A-Za-z]+\s+[0-9]{1,2},?\s+[0-9]{4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                date = matches[0].strip()
                return f"The date is {date}.", 0.9
        
        return "I couldn't find date information in this document.", 0.0
    
    def _find_batch_id(self, context: str) -> Tuple[str, float]:
        """Find batch ID from certificate"""
        batch_patterns = [
            r'batch\s+id[:\s]+([A-Za-z0-9\-]+)',
            r'batch[:\s]+([A-Za-z0-9\-]+)',
        ]
        
        for pattern in batch_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                batch_id = matches[0].strip()
                return f"The batch ID is {batch_id}.", 0.95
        
        return "I couldn't find the batch ID in this document.", 0.0
    
    def _find_farmer_info(self, context: str) -> Tuple[str, float]:
        """Find farmer information from certificate"""
        farmer_patterns = [
            r'farmer[:\s]+([A-Za-z\s]+?)(?:\s+Crop|$)',
            r'grower[:\s]+([A-Za-z\s]+?)(?:\s+Crop|$)',
        ]
        
        for pattern in farmer_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                farmer = matches[0].strip()
                # Clean up the farmer name (remove extra info)
                farmer = re.sub(r'\s+', ' ', farmer).strip()
                # Remove "Crop" if it got included
                farmer = re.sub(r'\s+Crop$', '', farmer).strip()
                if len(farmer) > 2 and len(farmer) < 50:
                    return f"The farmer is {farmer}.", 0.95
        
        return "I couldn't find farmer information in this document.", 0.0
    
    def _find_crop_info(self, context: str) -> Tuple[str, float]:
        """Find crop information from certificate"""
        crop_patterns = [
            r'crop[:\s]+([A-Za-z\s\-]+?)(?:\s+Quantity|$)',
        ]
        
        for pattern in crop_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                crop = matches[0].strip()
                # Clean up the crop name
                crop = re.sub(r'\s+', ' ', crop).strip()
                # Remove "Quantity" if it got included
                crop = re.sub(r'\s+Quantity$', '', crop).strip()
                if len(crop) > 2 and len(crop) < 50:
                    return f"The crop is {crop}.", 0.95
        
        return "I couldn't find crop information in this document.", 0.0
    
    def _find_quantity_info(self, context: str) -> Tuple[str, float]:
        """Find quantity information from certificate"""
        quantity_patterns = [
            r'quantity[:\s]+([0-9]+\s*[A-Za-z]+)',
            r'amount[:\s]+([0-9]+\s*[A-Za-z]+)',
        ]
        
        for pattern in quantity_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                quantity = matches[0].strip()
                return f"The quantity is {quantity}.", 0.95
        
        return "I couldn't find quantity information in this document.", 0.0
    
    def _find_group_id(self, context: str) -> Tuple[str, float]:
        """Find group ID from certificate"""
        group_patterns = [
            r'group\s+id[:\s]+([A-Za-z0-9\-]+)',
            r'group[:\s]+([A-Za-z0-9\-]+)',
        ]
        
        for pattern in group_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                group_id = matches[0].strip()
                return f"The group ID is {group_id}.", 0.95
        
        return "I couldn't find the group ID in this document.", 0.0
    
    def _find_group_name(self, context: str) -> Tuple[str, float]:
        """Find group name from certificate"""
        group_name_patterns = [
            r'group\s+name[:\s]+([A-Za-z0-9_\-]+)',
        ]
        
        for pattern in group_name_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                group_name = matches[0].strip()
                return f"The group name is {group_name}.", 0.95
        
        return "I couldn't find the group name in this document.", 0.0
    
    def _find_grading_info(self, context: str) -> Tuple[str, float]:
        """Find grading information from certificate"""
        grading_patterns = [
            r'grading[:\s]+([A-Za-z]+)',
            r'grade[:\s]+([A-Za-z]+)',
        ]
        
        for pattern in grading_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                grading = matches[0].strip()
                # Clean up the grading (remove extra words)
                grading = re.sub(r'\s+.*$', '', grading).strip()
                if len(grading) > 1 and len(grading) < 20:
                    return f"The grading is {grading}.", 0.95
        
        return "I couldn't find grading information in this document.", 0.0
    
    def _find_generated_date(self, context: str) -> Tuple[str, float]:
        """Find generated date from certificate"""
        generated_patterns = [
            r'generated[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2})',
            r'generated[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})',
        ]
        
        for pattern in generated_patterns:
            matches = re.findall(pattern, context, re.IGNORECASE)
            if matches:
                generated_date = matches[0].strip()
                return f"The generated date is {generated_date}.", 0.95
        
        return "I couldn't find the generated date in this document.", 0.0
    
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
        """Process a query and return the answer - FAST VERSION"""
        try:
            # Get document info for filename-based answers
            from app.models import Document, DocumentSection
            document = db.query(Document).filter(Document.id == document_id).first()
            
            # Check if we can answer from filename first (for author/title questions)
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
                    
                    self._log_activity(db, "query_asked", "query", query.id, {
                        "question": question,
                        "document_id": document_id,
                        "answer_source": "filename"
                    })
                    
                    return query
            elif 'title' in question_lower or 'name of the book' in question_lower:
                title_answer = self._extract_title_from_filename(document.filename if document else "")
                if title_answer:
                    query = Query(
                        document_id=document_id,
                        question=question,
                        answer=title_answer,
                        confidence_score=0.95
                    )
                    db.add(query)
                    db.commit()
                    
                    self._log_activity(db, "query_asked", "query", query.id, {
                        "question": question,
                        "document_id": document_id,
                        "answer_source": "filename"
                    })
                    
                    return query
            
            # Find relevant sections using fast keyword matching
            relevant_sections = document_processor.find_relevant_sections(db, document_id, question)
            
            if not relevant_sections:
                # No relevant sections found - get all sections for general overview
                all_sections = db.query(DocumentSection).filter(DocumentSection.document_id == document_id).all()
                if all_sections:
                    # Combine all sections for general overview
                    all_content = "\n\n".join([section.section_text for section in all_sections])
                    general_answer, confidence = self._provide_general_overview(all_content, question.lower())
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
                
                # Log the activity
                self._log_activity(db, "query_asked", "query", query.id, {
                    "question": question,
                    "document_id": document_id,
                    "relevant_sections_found": 0
                })
                
                return query
            
            # Combine relevant sections into context
            context = "\n\n".join([section.section_text for section in relevant_sections])
            
            # Get answer using fast keyword matching
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
    
    def _extract_author_from_filename(self, filename: str) -> str:
        """Extract author name from filename"""
        if not filename:
            return ""
        
        # Common patterns: "Author Name - Book Title.pdf"
        # Remove file extension
        name_without_ext = filename.replace('.pdf', '').replace('.txt', '').replace('.docx', '')
        
        # Split by common separators
        parts = re.split(r'\s*-\s*|\s*_\s*|\s*by\s*', name_without_ext)
        
        if len(parts) >= 2:
            # First part is usually the author
            author_part = parts[0].strip()
            
            # Clean up the author name
            author_part = re.sub(r'\s+', ' ', author_part)  # Remove extra spaces
            
            # Check if it looks like a name (has at least 2 words with capitals)
            words = author_part.split()
            if len(words) >= 2 and all(word[0].isupper() for word in words if word):
                return f"The author is {author_part}."
        
        return ""
    
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract book title from filename"""
        if not filename:
            return ""
        
        # Common patterns: "Author Name - Book Title.pdf"
        # Remove file extension
        name_without_ext = filename.replace('.pdf', '').replace('.txt', '').replace('.docx', '')
        
        # Split by common separators
        parts = re.split(r'\s*-\s*|\s*_\s*|\s*by\s*', name_without_ext)
        
        if len(parts) >= 2:
            # Second part is usually the title
            title_part = parts[1].strip()
            
            # Clean up the title
            title_part = re.sub(r'\s+', ' ', title_part)  # Remove extra spaces
            
            if len(title_part) > 3:  # Reasonable title length
                return f"The title is: {title_part}."
        
        return ""
    
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
