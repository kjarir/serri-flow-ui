import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Lead, ObjectionTemplate
from app.schemas import (
    ChatRequest, ChatResponse, LeadCreate, LeadResponse,
    DemoScheduleRequest, DemoScheduleResponse, ObjectionRequest,
    ObjectionResponse, FollowUpRequest, FollowUpResponse,
    ErrorResponse, SuccessResponse
)
from app.services.chatbot_service import ChatbotService
from app.services.objection_handler import ObjectionHandler
from app.services.calendly_service import CalendlyService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chatbot", tags=["Serri Chatbot"])

# Initialize services
chatbot_service = ChatbotService()
objection_handler = ObjectionHandler()
calendly_service = CalendlyService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Process a chat message and return bot response"""
    try:
        # Get or create lead
        lead = None
        if request.lead_id:
            lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
            if not lead:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Lead not found"
                )
        
        # Process message
        response, updated_lead, intent = chatbot_service.process_message(
            db, request.message, request.lead_id
        )
        
        # Determine next actions
        next_actions = []
        if intent == "demo_request" and updated_lead:
            next_actions.append("schedule_demo")
        elif intent in ["price_objection", "time_objection", "competitor_objection"]:
            next_actions.append("handle_objection")
        elif updated_lead and not updated_lead.demo_scheduled:
            next_actions.append("qualify_lead")
        
        return ChatResponse(
            response=response,
            intent=intent,
            lead_id=updated_lead.id if updated_lead else None,
            next_actions=next_actions
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chat processing failed"
        )


@router.post("/lead", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    db: Session = Depends(get_db)
):
    """Create a new lead"""
    try:
        lead = chatbot_service.create_lead(db, lead_data)
        
        return LeadResponse(
            id=lead.id,
            email=lead.email,
            name=lead.name,
            company=lead.company,
            industry=lead.industry,
            company_size=lead.company_size,
            role=lead.role,
            decision_making_power=lead.decision_making_power,
            interest_level=lead.interest_level,
            phone=lead.phone,
            demo_scheduled=lead.demo_scheduled,
            created_at=lead.created_at
        )
        
    except Exception as e:
        logger.error(f"Lead creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lead creation failed"
        )


@router.get("/leads", response_model=List[LeadResponse])
async def list_leads(db: Session = Depends(get_db)):
    """List all leads"""
    try:
        leads = db.query(Lead).order_by(Lead.created_at.desc()).all()
        
        return [
            LeadResponse(
                id=lead.id,
                email=lead.email,
                name=lead.name,
                company=lead.company,
                industry=lead.industry,
                company_size=lead.company_size,
                role=lead.role,
                decision_making_power=lead.decision_making_power,
                interest_level=lead.interest_level,
                phone=lead.phone,
                demo_scheduled=lead.demo_scheduled,
                created_at=lead.created_at
            )
            for lead in leads
        ]
        
    except Exception as e:
        logger.error(f"Failed to list leads: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list leads"
        )


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific lead"""
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        return LeadResponse(
            id=lead.id,
            email=lead.email,
            name=lead.name,
            company=lead.company,
            industry=lead.industry,
            company_size=lead.company_size,
            role=lead.role,
            decision_making_power=lead.decision_making_power,
            interest_level=lead.interest_level,
            phone=lead.phone,
            demo_scheduled=lead.demo_scheduled,
            created_at=lead.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get lead: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get lead"
        )


@router.post("/schedule-demo", response_model=DemoScheduleResponse)
async def schedule_demo(
    request: DemoScheduleRequest,
    db: Session = Depends(get_db)
):
    """Schedule a demo for a lead"""
    try:
        # Get lead
        lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Schedule demo
        result = await calendly_service.schedule_demo(db, lead, request.preferred_date)
        
        return DemoScheduleResponse(
            calendly_link=result["calendly_link"],
            event_id=result.get("event_id"),
            message=result["message"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Demo scheduling failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Demo scheduling failed"
        )


@router.post("/objection", response_model=ObjectionResponse)
async def handle_objection(
    request: ObjectionRequest,
    db: Session = Depends(get_db)
):
    """Handle an objection with pre-defined responses"""
    try:
        # Get lead if provided
        lead = None
        if request.lead_id:
            lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
        
        # Handle objection
        result = objection_handler.handle_objection(db, request.objection_type, request.lead_id)
        
        return ObjectionResponse(
            response=result["response"],
            follow_up_questions=result["follow_up_questions"]
        )
        
    except Exception as e:
        logger.error(f"Objection handling failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Objection handling failed"
        )


@router.post("/followup", response_model=FollowUpResponse)
async def send_followup(
    request: FollowUpRequest,
    db: Session = Depends(get_db)
):
    """Send a follow-up message to a lead"""
    try:
        # Get lead
        lead = db.query(Lead).filter(Lead.id == request.lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found"
            )
        
        # Send follow-up
        result = await calendly_service.send_reminder(db, lead, request.follow_up_type)
        
        return FollowUpResponse(
            message=result["message"],
            sent=result["sent"],
            method=result["method"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Follow-up sending failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Follow-up sending failed"
        )


@router.get("/objection-templates", response_model=List[dict])
async def get_objection_templates(db: Session = Depends(get_db)):
    """Get all objection templates"""
    try:
        templates = objection_handler.get_all_templates(db)
        
        return [
            {
                "id": template.id,
                "objection_type": template.objection_type,
                "template_response": template.template_response,
                "is_active": template.is_active,
                "created_at": template.created_at
            }
            for template in templates
        ]
        
    except Exception as e:
        logger.error(f"Failed to get objection templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get objection templates"
        )


@router.post("/objection-templates", response_model=dict)
async def create_objection_template(
    objection_type: str,
    template_response: str,
    db: Session = Depends(get_db)
):
    """Create a new objection template"""
    try:
        template = objection_handler.create_objection_template(
            db, objection_type, template_response
        )
        
        return {
            "id": template.id,
            "objection_type": template.objection_type,
            "template_response": template.template_response,
            "is_active": template.is_active,
            "created_at": template.created_at
        }
        
    except Exception as e:
        logger.error(f"Failed to create objection template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create objection template"
        )
