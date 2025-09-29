from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10), nullable=False)  # PDF, TXT
    content = Column(Text, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sections = relationship("DocumentSection", back_populates="document", cascade="all, delete-orphan")
    queries = relationship("Query", back_populates="document", cascade="all, delete-orphan")


class DocumentSection(Base):
    __tablename__ = "document_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    section_text = Column(Text, nullable=False)
    section_index = Column(Integer, nullable=False)
    embedding = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="sections")


class Query(Base):
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    feedback = Column(String(20), nullable=True)  # "good", "not_helpful", "too_vague"
    iteration_count = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="queries")


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=True)
    company = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)  # "1-10", "11-50", "51-200", "200+"
    role = Column(String(100), nullable=True)
    decision_making_power = Column(String(50), nullable=True)  # "low", "medium", "high"
    interest_level = Column(String(50), nullable=True)  # "low", "medium", "high"
    phone = Column(String(20), nullable=True)
    demo_scheduled = Column(Boolean, default=False)
    calendly_event_id = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    message_type = Column(String(50), nullable=False)  # "user", "bot", "system"
    intent = Column(String(100), nullable=True)  # "qualification", "objection", "demo_request", etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="conversations")


class ObjectionTemplate(Base):
    __tablename__ = "objection_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    objection_type = Column(String(100), nullable=False)  # "price", "time", "competitor", etc.
    template_response = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    action = Column(String(100), nullable=False)  # "document_uploaded", "query_asked", "feedback_given", etc.
    entity_type = Column(String(50), nullable=False)  # "document", "query", "lead", etc.
    entity_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
