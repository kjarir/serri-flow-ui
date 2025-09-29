#!/usr/bin/env python3
"""
Quick start script for Serri Flow Backend
This script sets up a minimal environment to get the backend running quickly
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_sqlite_db():
    """Create a SQLite database for quick testing"""
    db_path = "serri_flow.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Create SQLite database
    conn = sqlite3.connect(db_path)
    conn.close()
    
    # Update the database URL in config
    config_content = '''from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database - Using SQLite for quick start
    database_url: str = "sqlite:///./serri_flow.db"
    
    # API Keys
    api_key: str = "your-secret-api-key-here"
    calendly_api_token: Optional[str] = None
    huggingface_api_token: Optional[str] = None
    
    # App Settings
    debug: bool = True
    log_level: str = "INFO"
    
    # AI Model Settings
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    qa_model: str = "distilbert-base-uncased-distilled-squad"
    
    class Config:
        env_file = ".env"


settings = Settings()'''
    
    with open("app/config.py", "w") as f:
        f.write(config_content)
    
    print("✅ Created SQLite database and updated config")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    return True

def create_tables():
    """Create database tables"""
    print("🗄️ Creating database tables...")
    try:
        # Import and create tables
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from app.database import engine, Base
        from app.models import (
            Document, DocumentSection, Query, Lead, Conversation, 
            ObjectionTemplate, ActivityLog
        )
        
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    return True

def create_sample_data():
    """Create sample data"""
    print("🌱 Creating sample data...")
    try:
        from app.database import SessionLocal
        from app.models import ObjectionTemplate, ActivityLog
        
        db = SessionLocal()
        
        # Create objection templates
        templates = [
            ObjectionTemplate(
                objection_type="price",
                template_response="I understand budget is important. Let me show you the ROI - our clients typically save 40% on support costs within 3 months."
            ),
            ObjectionTemplate(
                objection_type="time",
                template_response="I completely understand being busy - that's exactly why you need this! Our solution saves 10+ hours per week."
            ),
            ObjectionTemplate(
                objection_type="competitor",
                template_response="That's great you're exploring options! What specific features are you looking for? I can show you how we compare."
            )
        ]
        
        for template in templates:
            db.add(template)
        
        # Create activity log
        log = ActivityLog(
            action="system_startup",
            entity_type="system",
            entity_id=None,
            details={"message": "Serri Flow Backend started successfully"}
        )
        db.add(log)
        
        db.commit()
        db.close()
        
        print("✅ Sample data created")
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False
    return True

def main():
    """Main setup function"""
    print("🚀 Quick Start Setup for Serri Flow Backend")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    print("✅ Created uploads directory")
    
    # Create SQLite database
    create_sqlite_db()
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return
    
    # Create tables
    if not create_tables():
        print("❌ Setup failed at table creation")
        return
    
    # Create sample data
    if not create_sample_data():
        print("❌ Setup failed at sample data creation")
        return
    
    print("\n🎉 Quick start setup completed!")
    print("\nNext steps:")
    print("1. Start the backend: python run.py")
    print("2. The API will be available at: http://localhost:8000")
    print("3. API Documentation: http://localhost:8000/docs")
    print("\nNote: This setup uses SQLite for quick testing.")
    print("For production, configure PostgreSQL in the .env file.")

if __name__ == "__main__":
    main()
