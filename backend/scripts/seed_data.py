#!/usr/bin/env python3
"""
Seed script for Serri Flow Backend
Creates sample data for testing and demonstration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, ObjectionTemplate, Lead, ActivityLog
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_objection_templates(db: Session):
    """Create sample objection templates"""
    templates = [
        {
            "objection_type": "price",
            "template_response": "I understand budget is important. Let me show you the ROI - our clients typically save 40% on support costs within 3 months. What's your current monthly support cost?"
        },
        {
            "objection_type": "time",
            "template_response": "I completely understand being busy - that's exactly why you need this! Our solution saves 10+ hours per week. A 15-minute demo could save you hours every week. What's your email for a quick calendar invite?"
        },
        {
            "objection_type": "competitor",
            "template_response": "That's great you're exploring options! What specific features are you looking for? I can show you how we compare. Our AI is trained specifically for customer support, unlike generic solutions."
        },
        {
            "objection_type": "trust",
            "template_response": "I understand the hesitation with new technology. We have 500+ satisfied clients and 99.9% uptime. We offer a 30-day free trial with full support. You can test it risk-free."
        },
        {
            "objection_type": "need",
            "template_response": "That's interesting - what's your current process for handling customer questions? How many support requests do you get per day? Even small teams can benefit from AI assistance."
        }
    ]
    
    for template_data in templates:
        existing = db.query(ObjectionTemplate).filter(
            ObjectionTemplate.objection_type == template_data["objection_type"]
        ).first()
        
        if not existing:
            template = ObjectionTemplate(**template_data)
            db.add(template)
            logger.info(f"Created objection template for {template_data['objection_type']}")
        else:
            logger.info(f"Objection template for {template_data['objection_type']} already exists")
    
    db.commit()


def create_sample_leads(db: Session):
    """Create sample leads for testing"""
    sample_leads = [
        {
            "email": "john.doe@techcorp.com",
            "name": "John Doe",
            "company": "TechCorp Inc",
            "industry": "tech",
            "company_size": "51-200",
            "role": "CTO",
            "decision_making_power": "high",
            "interest_level": "high",
            "phone": "+1-555-0123"
        },
        {
            "email": "sarah.smith@healthplus.com",
            "name": "Sarah Smith",
            "company": "HealthPlus Medical",
            "industry": "healthcare",
            "company_size": "11-50",
            "role": "Operations Manager",
            "decision_making_power": "medium",
            "interest_level": "medium",
            "phone": "+1-555-0456"
        },
        {
            "email": "mike.johnson@retailstore.com",
            "name": "Mike Johnson",
            "company": "RetailStore Chain",
            "industry": "retail",
            "company_size": "200+",
            "role": "Customer Service Director",
            "decision_making_power": "high",
            "interest_level": "high",
            "phone": "+1-555-0789"
        },
        {
            "email": "lisa.brown@startup.io",
            "name": "Lisa Brown",
            "company": "StartupIO",
            "industry": "tech",
            "company_size": "1-10",
            "role": "Founder",
            "decision_making_power": "high",
            "interest_level": "medium",
            "phone": "+1-555-0321"
        }
    ]
    
    for lead_data in sample_leads:
        existing = db.query(Lead).filter(Lead.email == lead_data["email"]).first()
        
        if not existing:
            lead = Lead(**lead_data)
            db.add(lead)
            logger.info(f"Created sample lead: {lead_data['email']}")
        else:
            logger.info(f"Lead {lead_data['email']} already exists")
    
    db.commit()


def create_sample_activity_logs(db: Session):
    """Create sample activity logs"""
    sample_logs = [
        {
            "action": "system_startup",
            "entity_type": "system",
            "entity_id": None,
            "details": {"message": "Serri Flow Backend started successfully"}
        },
        {
            "action": "seed_data_loaded",
            "entity_type": "system",
            "entity_id": None,
            "details": {"templates_created": 5, "leads_created": 4}
        }
    ]
    
    for log_data in sample_logs:
        log = ActivityLog(**log_data)
        db.add(log)
        logger.info(f"Created activity log: {log_data['action']}")
    
    db.commit()


def main():
    """Main seed function"""
    logger.info("Starting seed data creation...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create objection templates
        logger.info("Creating objection templates...")
        create_objection_templates(db)
        
        # Create sample leads
        logger.info("Creating sample leads...")
        create_sample_leads(db)
        
        # Create sample activity logs
        logger.info("Creating sample activity logs...")
        create_sample_activity_logs(db)
        
        logger.info("Seed data creation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during seed data creation: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
