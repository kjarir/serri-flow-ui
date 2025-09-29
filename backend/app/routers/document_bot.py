import os
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Document, Query, ActivityLog
from app.schemas import (
    DocumentUploadResponse, QueryRequest, QueryResponse, 
    FeedbackRequest, LogEntry, ErrorResponse, SuccessResponse
)
from app.services.ml_processor import MLDocumentProcessor
from app.services.universal_ml_qa import UniversalMLQA

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/document-bot", tags=["Document Bot"])

# Initialize universal ML services
document_processor = MLDocumentProcessor()
qa_service = UniversalMLQA()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-doc", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF or TXT document for processing"""
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )
        
        file_extension = file.filename.split('.')[-1].lower()
        if file_extension not in ['pdf', 'txt']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF and TXT files are supported"
            )
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Create document record
        document = Document(
            filename=file.filename,
            file_path=file_path,
            file_type=file_extension.upper(),
            content=""  # Will be filled during processing
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Process document with ML
        try:
            doc_id = document_processor.process_document(file_path, db)
            return DocumentUploadResponse(
                doc_id=doc_id,
                filename=document.filename,
                message="Document uploaded and processed successfully with ML"
            )
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document processing failed: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Upload failed"
        )


@router.post("/ask-query", response_model=QueryResponse)
async def ask_query(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """Ask a question about a document"""
    try:
        # Check if document exists and is processed
        document = db.query(Document).filter(Document.id == request.doc_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if not document.processed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is still being processed. Please try again in a moment."
            )
        
        # Process query
        query = qa_service.process_query(db, request.doc_id, request.query, document_processor)
        
        return QueryResponse(
            answer=query.answer,
            confidence_score=query.confidence_score,
            iteration_count=query.iteration_count,
            feedback_options=["good", "not_helpful", "too_vague"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Query processing failed"
        )


@router.post("/feedback", response_model=SuccessResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
):
    """Submit feedback on a query response"""
    try:
        # Validate feedback
        if request.feedback not in ["good", "not_helpful", "too_vague"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid feedback. Must be one of: good, not_helpful, too_vague"
            )
        
        # Handle feedback
        updated_query = qa_service.handle_feedback(db, request.query_id, request.feedback)
        
        return SuccessResponse(
            message="Feedback submitted successfully",
            data={
                "query_id": updated_query.id,
                "feedback": updated_query.feedback,
                "iteration_count": updated_query.iteration_count,
                "updated_answer": updated_query.answer
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback submission failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Feedback submission failed"
        )


@router.get("/logs/{doc_id}", response_model=List[LogEntry])
async def get_document_logs(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """Get activity logs for a document"""
    try:
        # Check if document exists
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Get logs related to this document
        logs = db.query(ActivityLog).filter(
            ActivityLog.entity_type == "document",
            ActivityLog.entity_id == doc_id
        ).order_by(ActivityLog.created_at.desc()).all()
        
        # Also get logs for queries related to this document
        query_logs = db.query(ActivityLog).join(Query).filter(
            Query.document_id == doc_id
        ).order_by(ActivityLog.created_at.desc()).all()
        
        all_logs = logs + query_logs
        
        return [
            LogEntry(
                id=log.id,
                action=log.action,
                entity_type=log.entity_type,
                entity_id=log.entity_id,
                details=log.details,
                created_at=log.created_at
            )
            for log in all_logs
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get logs"
        )


@router.get("/documents", response_model=List[dict])
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    try:
        documents = db.query(Document).order_by(Document.created_at.desc()).all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "processed": doc.processed,
                "created_at": doc.created_at,
                "query_count": len(doc.queries)
            }
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents"
        )


@router.get("/queries/{doc_id}", response_model=List[dict])
async def get_document_queries(
    doc_id: int,
    db: Session = Depends(get_db)
):
    """Get all queries for a document"""
    try:
        # Check if document exists
        document = db.query(Document).filter(Document.id == doc_id).first()
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        queries = db.query(Query).filter(
            Query.document_id == doc_id
        ).order_by(Query.created_at.desc()).all()
        
        return [
            {
                "id": query.id,
                "question": query.question,
                "answer": query.answer,
                "confidence_score": query.confidence_score,
                "feedback": query.feedback,
                "iteration_count": query.iteration_count,
                "created_at": query.created_at
            }
            for query in queries
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get queries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get queries"
        )
