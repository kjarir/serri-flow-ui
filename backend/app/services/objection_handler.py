import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models import ObjectionTemplate, Lead, ActivityLog

logger = logging.getLogger(__name__)


class ObjectionHandler:
    def __init__(self):
        self.objection_responses = {
            "price": {
                "templates": [
                    "I understand budget is important. Let me show you the ROI - our clients typically save 40% on support costs within 3 months.",
                    "What's your current cost per support ticket? Our solution often pays for itself by reducing ticket volume by 60%.",
                    "We offer flexible pricing options. What's your monthly support budget? I can show you a plan that fits."
                ],
                "follow_up_questions": [
                    "What's your current monthly support cost?",
                    "How many support tickets do you handle per month?",
                    "What's the cost of one support agent per month?"
                ]
            },
            "time": {
                "templates": [
                    "I completely understand being busy - that's exactly why you need this! Our solution saves 10+ hours per week.",
                    "A 15-minute demo could save you hours every week. What's your email for a quick calendar invite?",
                    "The setup takes just 30 minutes, and you'll see results immediately. When's a good time this week?"
                ],
                "follow_up_questions": [
                    "How much time do you currently spend on support tasks?",
                    "What's your biggest time waster in customer support?",
                    "When would be a good 15-minute window this week?"
                ]
            },
            "competitor": {
                "templates": [
                    "That's great you're exploring options! What specific features are you looking for? I can show you how we compare.",
                    "Our AI is trained specifically for customer support, unlike generic solutions. What's your main use case?",
                    "We offer 24/7 support and custom training. What's most important to you - accuracy, speed, or customization?"
                ],
                "follow_up_questions": [
                    "What other solutions are you considering?",
                    "What's most important to you in a support solution?",
                    "Have you tried other AI solutions before?"
                ]
            },
            "trust": {
                "templates": [
                    "I understand the hesitation with new technology. We have 500+ satisfied clients and 99.9% uptime.",
                    "We offer a 30-day free trial with full support. You can test it risk-free. What's your email?",
                    "Our AI is trained on millions of support conversations and continuously improves. Would you like to see some case studies?"
                ],
                "follow_up_questions": [
                    "What concerns do you have about AI solutions?",
                    "Have you had bad experiences with automation before?",
                    "What would make you feel more confident about trying our solution?"
                ]
            },
            "need": {
                "templates": [
                    "That's interesting - what's your current process for handling customer questions?",
                    "How many support requests do you get per day? Even small teams can benefit from AI assistance.",
                    "Our solution works for companies of any size. What's your biggest support challenge right now?"
                ],
                "follow_up_questions": [
                    "How do you currently handle customer support?",
                    "What's your biggest support challenge?",
                    "How many people are on your support team?"
                ]
            }
        }
    
    def detect_objection_type(self, message: str) -> str:
        """Detect the type of objection from the message"""
        message_lower = message.lower()
        
        # Price objections
        if any(word in message_lower for word in ["expensive", "costly", "budget", "can't afford", "too much", "price"]):
            return "price"
        
        # Time objections
        if any(word in message_lower for word in ["time", "busy", "schedule", "later", "no time", "rushed"]):
            return "time"
        
        # Competitor objections
        if any(word in message_lower for word in ["competitor", "alternative", "other solution", "already using", "different tool"]):
            return "competitor"
        
        # Trust objections
        if any(word in message_lower for word in ["trust", "reliable", "proven", "new", "risky", "uncertain"]):
            return "trust"
        
        # Need objections
        if any(word in message_lower for word in ["don't need", "not necessary", "fine without", "working fine"]):
            return "need"
        
        return "general"
    
    def get_objection_response(self, objection_type: str, lead: Optional[Lead] = None) -> Dict[str, any]:
        """Get response template and follow-up questions for an objection"""
        try:
            if objection_type in self.objection_responses:
                response_data = self.objection_responses[objection_type]
                
                # Select template based on lead context if available
                template = response_data["templates"][0]  # Default to first template
                if lead:
                    # Customize based on lead information
                    if lead.company_size and objection_type == "price":
                        if lead.company_size in ["1-10", "11-50"]:
                            template = response_data["templates"][1]  # Focus on ROI
                        else:
                            template = response_data["templates"][0]  # Focus on savings
                
                return {
                    "response": template,
                    "follow_up_questions": response_data["follow_up_questions"],
                    "objection_type": objection_type
                }
            else:
                return {
                    "response": "I understand your concern. Could you tell me more about what's holding you back?",
                    "follow_up_questions": ["What's your biggest concern?", "What would make this decision easier?"],
                    "objection_type": "general"
                }
                
        except Exception as e:
            logger.error(f"Failed to get objection response: {e}")
            return {
                "response": "I understand your concern. Let me know how I can help address it.",
                "follow_up_questions": [],
                "objection_type": "general"
            }
    
    def handle_objection(self, db: Session, message: str, lead_id: Optional[int] = None) -> Dict[str, any]:
        """Handle an objection and return appropriate response"""
        try:
            # Get lead if provided
            lead = None
            if lead_id:
                lead = db.query(Lead).filter(Lead.id == lead_id).first()
            
            # Detect objection type
            objection_type = self.detect_objection_type(message)
            
            # Get response
            response_data = self.get_objection_response(objection_type, lead)
            
            # Log the objection handling
            if lead:
                self._log_activity(db, "objection_handled", "lead", lead.id, {
                    "objection_type": objection_type,
                    "message": message,
                    "response": response_data["response"]
                })
            
            logger.info(f"Handled {objection_type} objection for lead {lead_id}")
            return response_data
            
        except Exception as e:
            logger.error(f"Failed to handle objection: {e}")
            return {
                "response": "I understand your concern. Let me know how I can help address it.",
                "follow_up_questions": [],
                "objection_type": "general"
            }
    
    def create_objection_template(self, db: Session, objection_type: str, template_response: str) -> ObjectionTemplate:
        """Create a new objection template"""
        try:
            template = ObjectionTemplate(
                objection_type=objection_type,
                template_response=template_response
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            
            logger.info(f"Created objection template for {objection_type}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create objection template: {e}")
            raise
    
    def get_all_templates(self, db: Session) -> List[ObjectionTemplate]:
        """Get all active objection templates"""
        try:
            return db.query(ObjectionTemplate).filter(ObjectionTemplate.is_active == True).all()
        except Exception as e:
            logger.error(f"Failed to get objection templates: {e}")
            return []
    
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
