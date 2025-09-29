from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime


# Document Bot Schemas
class DocumentUploadResponse(BaseModel):
    doc_id: int
    filename: str
    message: str


class QueryRequest(BaseModel):
    doc_id: int
    query: str


class QueryResponse(BaseModel):
    answer: str
    confidence_score: Optional[float] = None
    iteration_count: int = 1
    feedback_options: List[str] = ["good", "not_helpful", "too_vague"]


class FeedbackRequest(BaseModel):
    query_id: int
    feedback: str  # "good", "not_helpful", "too_vague"


class LogEntry(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: Optional[int]
    details: Optional[Dict[str, Any]]
    created_at: datetime


# Serri Chatbot Schemas
class ChatRequest(BaseModel):
    message: str
    lead_id: Optional[int] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    intent: Optional[str] = None
    lead_id: Optional[int] = None
    next_actions: Optional[List[str]] = None


class LeadCreate(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    role: Optional[str] = None
    decision_making_power: Optional[str] = None
    interest_level: Optional[str] = None
    phone: Optional[str] = None


class LeadResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    company: Optional[str]
    industry: Optional[str]
    company_size: Optional[str]
    role: Optional[str]
    decision_making_power: Optional[str]
    interest_level: Optional[str]
    phone: Optional[str]
    demo_scheduled: bool
    created_at: datetime


class DemoScheduleRequest(BaseModel):
    lead_id: int
    preferred_date: Optional[str] = None
    timezone: Optional[str] = "UTC"


class DemoScheduleResponse(BaseModel):
    calendly_link: str
    event_id: Optional[str] = None
    message: str


class ObjectionRequest(BaseModel):
    objection_type: str
    lead_id: Optional[int] = None
    context: Optional[str] = None


class ObjectionResponse(BaseModel):
    response: str
    follow_up_questions: Optional[List[str]] = None


class FollowUpRequest(BaseModel):
    lead_id: int
    follow_up_type: str  # "demo_reminder", "objection_follow_up", "general"


class FollowUpResponse(BaseModel):
    message: str
    sent: bool
    method: str  # "email", "whatsapp", "sms"


# Common Schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None
