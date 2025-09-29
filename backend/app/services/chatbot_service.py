import logging
import re
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Lead, Conversation, ActivityLog
from app.schemas import LeadCreate

logger = logging.getLogger(__name__)


class ChatbotService:
    def __init__(self):
        self.qualification_questions = {
            "industry": "What industry is your company in?",
            "company_size": "How many employees does your company have? (1-10, 11-50, 51-200, 200+)",
            "role": "What's your role in the company?",
            "decision_making_power": "Are you involved in making decisions about software purchases? (low/medium/high)",
            "interest_level": "How interested are you in our AI solution? (low/medium/high)"
        }
        
        self.qualification_keywords = {
            "industry": {
                "tech": ["technology", "software", "tech", "IT", "computer", "digital"],
                "healthcare": ["healthcare", "medical", "hospital", "clinic", "pharmaceutical"],
                "finance": ["finance", "banking", "financial", "investment", "insurance"],
                "retail": ["retail", "ecommerce", "shopping", "store", "commerce"],
                "manufacturing": ["manufacturing", "production", "factory", "industrial"],
                "education": ["education", "school", "university", "learning", "training"]
            },
            "company_size": {
                "1-10": ["1-10", "small", "startup", "few", "less than 10"],
                "11-50": ["11-50", "small-medium", "growing", "medium"],
                "51-200": ["51-200", "medium", "established"],
                "200+": ["200+", "large", "enterprise", "big", "corporation"]
            },
            "decision_making_power": {
                "high": ["high", "decision maker", "CEO", "CTO", "director", "manager", "lead"],
                "medium": ["medium", "influence", "recommend", "suggest", "team lead"],
                "low": ["low", "employee", "staff", "user", "not involved"]
            },
            "interest_level": {
                "high": ["high", "very interested", "definitely", "yes", "sure", "interested"],
                "medium": ["medium", "somewhat", "maybe", "considering", "curious"],
                "low": ["low", "not really", "just looking", "browsing", "not sure"]
            }
        }
    
    def detect_intent(self, message: str) -> str:
        """Detect the intent of the user's message"""
        message_lower = message.lower()
        
        # Demo request
        if any(word in message_lower for word in ["demo", "demonstration", "show me", "trial", "test"]):
            return "demo_request"
        
        # Pricing questions
        if any(word in message_lower for word in ["price", "cost", "pricing", "how much", "expensive"]):
            return "pricing_inquiry"
        
        # Objections
        if any(word in message_lower for word in ["expensive", "costly", "budget", "can't afford"]):
            return "price_objection"
        if any(word in message_lower for word in ["time", "busy", "schedule", "later"]):
            return "time_objection"
        if any(word in message_lower for word in ["competitor", "alternative", "other solution"]):
            return "competitor_objection"
        
        # General questions
        if any(word in message_lower for word in ["what", "how", "why", "when", "where"]):
            return "general_question"
        
        # Greeting
        if any(word in message_lower for word in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            return "greeting"
        
        return "unknown"
    
    def extract_qualification_info(self, message: str, current_lead: Optional[Lead] = None) -> Dict[str, Optional[str]]:
        """Extract qualification information from the message"""
        message_lower = message.lower()
        extracted = {}
        
        # Extract industry
        for industry, keywords in self.qualification_keywords["industry"].items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["industry"] = industry
                break
        
        # Extract company size
        for size, keywords in self.qualification_keywords["company_size"].items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["company_size"] = size
                break
        
        # Extract decision making power
        for power, keywords in self.qualification_keywords["decision_making_power"].items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["decision_making_power"] = power
                break
        
        # Extract interest level
        for interest, keywords in self.qualification_keywords["interest_level"].items():
            if any(keyword in message_lower for keyword in keywords):
                extracted["interest_level"] = interest
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, message)
        if email_match:
            extracted["email"] = email_match.group()
        
        # Extract phone
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            extracted["phone"] = phone_match.group()
        
        return extracted
    
    def get_next_qualification_question(self, lead: Lead) -> Optional[str]:
        """Get the next qualification question based on what's missing"""
        if not lead.industry:
            return self.qualification_questions["industry"]
        if not lead.company_size:
            return self.qualification_questions["company_size"]
        if not lead.role:
            return self.qualification_questions["role"]
        if not lead.decision_making_power:
            return self.qualification_questions["decision_making_power"]
        if not lead.interest_level:
            return self.qualification_questions["interest_level"]
        return None
    
    def generate_response(self, message: str, intent: str, lead: Optional[Lead] = None) -> str:
        """Generate appropriate response based on intent and lead status"""
        if intent == "greeting":
            return "Hello! I'm Serri, your AI assistant. I'm here to help you learn about our AI-powered solutions. What brings you here today?"
        
        elif intent == "demo_request":
            if lead and lead.demo_scheduled:
                return "Great! I see you already have a demo scheduled. Is there anything specific you'd like to know before our meeting?"
            return "I'd love to schedule a demo for you! Let me get some quick information first. What's your email address?"
        
        elif intent == "pricing_inquiry":
            return "Our pricing is customized based on your specific needs and company size. I'd be happy to discuss this during a demo. What's your company size?"
        
        elif intent == "price_objection":
            return "I understand budget is always a consideration. Our solution actually helps companies save money by automating processes and reducing manual work. What's your current process for handling customer support?"
        
        elif intent == "time_objection":
            return "I completely understand being busy! That's exactly why our solution is so valuable - it saves you time. A quick 15-minute demo could show you how to save hours every week. What's your email?"
        
        elif intent == "competitor_objection":
            return "That's great that you're exploring options! What specific features are you looking for? I can show you how Serri compares and what makes us unique."
        
        elif intent == "general_question":
            return "I'd be happy to answer your questions! Could you tell me a bit about your company and what challenges you're facing with customer support?"
        
        else:
            # Try to extract qualification info
            if lead:
                extracted = self.extract_qualification_info(message, lead)
                if extracted:
                    # Update lead with extracted info
                    for key, value in extracted.items():
                        if hasattr(lead, key) and value:
                            setattr(lead, key, value)
                    
                    # Get next question
                    next_question = self.get_next_qualification_question(lead)
                    if next_question:
                        return f"Thanks for that information! {next_question}"
                    else:
                        return "Perfect! I have all the information I need. Would you like to schedule a demo to see how Serri can help your company?"
            
            return "I'd love to help you learn more about Serri! Could you tell me what industry your company is in?"
    
    def process_message(self, db: Session, message: str, lead_id: Optional[int] = None) -> Tuple[str, Optional[Lead], str]:
        """Process a user message and return response, lead, and intent"""
        try:
            # Get or create lead
            lead = None
            if lead_id:
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
            
            # Detect intent
            intent = self.detect_intent(message)
            
            # Extract qualification information
            if lead:
                extracted = self.extract_qualification_info(message, lead)
                for key, value in extracted.items():
                    if hasattr(lead, key) and value:
                        setattr(lead, key, value)
                db.commit()
            
            # Generate response
            response = self.generate_response(message, intent, lead)
            
            # Save conversation
            if lead:
                conversation = Conversation(
                    lead_id=lead.id,
                    message=message,
                    response=response,
                    message_type="user",
                    intent=intent
                )
                db.add(conversation)
                
                # Add bot response
                bot_conversation = Conversation(
                    lead_id=lead.id,
                    message=response,
                    response=None,
                    message_type="bot",
                    intent=intent
                )
                db.add(bot_conversation)
                db.commit()
                
                # Log activity
                self._log_activity(db, "message_processed", "conversation", conversation.id, {
                    "intent": intent,
                    "lead_id": lead.id,
                    "message_length": len(message)
                })
            
            return response, lead, intent
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
            return "I apologize, but I encountered an error. Please try again.", lead, "error"
    
    def create_lead(self, db: Session, lead_data: LeadCreate) -> Lead:
        """Create a new lead"""
        try:
            # Check if lead already exists
            existing_lead = db.query(Lead).filter(Lead.email == lead_data.email).first()
            if existing_lead:
                return existing_lead
            
            lead = Lead(**lead_data.dict())
            db.add(lead)
            db.commit()
            db.refresh(lead)
            
            # Log activity
            self._log_activity(db, "lead_created", "lead", lead.id, {
                "email": lead.email,
                "company": lead.company
            })
            
            logger.info(f"Created new lead: {lead.email}")
            return lead
            
        except Exception as e:
            logger.error(f"Failed to create lead: {e}")
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
