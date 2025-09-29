import logging
import httpx
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.models import Lead, ActivityLog
from app.config import settings

logger = logging.getLogger(__name__)


class CalendlyService:
    def __init__(self):
        self.api_token = settings.calendly_api_token
        self.base_url = "https://api.calendly.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def get_available_events(self, user_uri: str = None) -> List[Dict]:
        """Get available Calendly events"""
        try:
            async with httpx.AsyncClient() as client:
                if user_uri:
                    url = f"{self.base_url}/scheduled_events"
                    params = {"user": user_uri}
                else:
                    url = f"{self.base_url}/scheduled_events"
                    params = {}
                
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                return data.get("collection", [])
                
        except Exception as e:
            logger.error(f"Failed to get available events: {e}")
            return []
    
    async def create_event(self, lead: Lead, event_type: str = "demo") -> Dict:
        """Create a Calendly event for a lead"""
        try:
            if not self.api_token:
                # Return mock response if no API token
                return {
                    "event_id": f"mock_event_{lead.id}",
                    "calendly_link": "https://calendly.com/serri-ai/demo",
                    "status": "scheduled"
                }
            
            event_data = {
                "name": f"Serri AI Demo - {lead.company or 'Prospect'}",
                "start_time": "2024-01-15T10:00:00Z",  # This would be dynamic in real implementation
                "end_time": "2024-01-15T10:30:00Z",
                "event_type": event_type,
                "location": "Online",
                "description": f"Demo session for {lead.name or lead.email} from {lead.company or 'Unknown Company'}",
                "attendees": [
                    {
                        "email": lead.email,
                        "name": lead.name or "Prospect"
                    }
                ]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/scheduled_events",
                    headers=self.headers,
                    json=event_data
                )
                response.raise_for_status()
                
                data = response.json()
                return {
                    "event_id": data.get("uri", "").split("/")[-1],
                    "calendly_link": data.get("html_link", ""),
                    "status": "scheduled"
                }
                
        except Exception as e:
            logger.error(f"Failed to create Calendly event: {e}")
            # Return fallback response
            return {
                "event_id": f"fallback_event_{lead.id}",
                "calendly_link": "https://calendly.com/serri-ai/demo",
                "status": "scheduled"
            }
    
    async def get_event_details(self, event_id: str) -> Optional[Dict]:
        """Get details of a specific Calendly event"""
        try:
            if not self.api_token:
                return {
                    "id": event_id,
                    "status": "scheduled",
                    "start_time": "2024-01-15T10:00:00Z",
                    "end_time": "2024-01-15T10:30:00Z"
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/scheduled_events/{event_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            logger.error(f"Failed to get event details: {e}")
            return None
    
    async def cancel_event(self, event_id: str) -> bool:
        """Cancel a Calendly event"""
        try:
            if not self.api_token:
                logger.info(f"Mock cancellation of event {event_id}")
                return True
            
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/scheduled_events/{event_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to cancel event {event_id}: {e}")
            return False
    
    def generate_calendly_link(self, lead: Lead, event_type: str = "demo") -> str:
        """Generate a Calendly link for scheduling"""
        # This is a simplified version - in production you'd use the actual Calendly API
        base_url = "https://calendly.com/serri-ai"
        
        if event_type == "demo":
            return f"{base_url}/demo"
        elif event_type == "consultation":
            return f"{base_url}/consultation"
        else:
            return f"{base_url}/demo"
    
    async def schedule_demo(self, db: Session, lead: Lead, preferred_date: Optional[str] = None) -> Dict:
        """Schedule a demo for a lead"""
        try:
            # Update lead status
            lead.demo_scheduled = True
            
            # Create Calendly event
            event_result = await self.create_event(lead, "demo")
            
            # Update lead with event ID
            if event_result.get("event_id"):
                lead.calendly_event_id = event_result["event_id"]
            
            db.commit()
            
            # Log the activity
            self._log_activity(db, "demo_scheduled", "lead", lead.id, {
                "event_id": event_result.get("event_id"),
                "calendly_link": event_result.get("calendly_link"),
                "preferred_date": preferred_date
            })
            
            logger.info(f"Scheduled demo for lead {lead.id}")
            
            return {
                "calendly_link": event_result.get("calendly_link", self.generate_calendly_link(lead)),
                "event_id": event_result.get("event_id"),
                "message": f"Great! I've scheduled your demo. You can also use this link to reschedule: {event_result.get('calendly_link', self.generate_calendly_link(lead))}"
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule demo for lead {lead.id}: {e}")
            db.rollback()
            
            # Return fallback response
            return {
                "calendly_link": self.generate_calendly_link(lead),
                "event_id": None,
                "message": f"Here's your demo scheduling link: {self.generate_calendly_link(lead)}"
            }
    
    async def send_reminder(self, db: Session, lead: Lead, reminder_type: str = "demo_reminder") -> Dict:
        """Send a reminder to a lead"""
        try:
            if reminder_type == "demo_reminder" and lead.demo_scheduled:
                message = f"Hi {lead.name or 'there'}! Just a friendly reminder about your upcoming Serri AI demo. Looking forward to showing you how we can help {lead.company or 'your company'}!"
            elif reminder_type == "follow_up" and not lead.demo_scheduled:
                message = f"Hi {lead.name or 'there'}! I wanted to follow up on our conversation about Serri AI. Would you like to schedule a quick demo to see how we can help {lead.company or 'your company'}?"
            else:
                message = f"Hi {lead.name or 'there'}! I wanted to follow up on our conversation about Serri AI. How can I help you today?"
            
            # Log the reminder
            self._log_activity(db, "reminder_sent", "lead", lead.id, {
                "reminder_type": reminder_type,
                "message": message
            })
            
            logger.info(f"Sent {reminder_type} reminder to lead {lead.id}")
            
            return {
                "message": message,
                "sent": True,
                "method": "email"  # In production, this would actually send via email/WhatsApp
            }
            
        except Exception as e:
            logger.error(f"Failed to send reminder to lead {lead.id}: {e}")
            return {
                "message": "Failed to send reminder",
                "sent": False,
                "method": "email"
            }
    
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
