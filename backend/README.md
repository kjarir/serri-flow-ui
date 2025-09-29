# Serri Flow Backend

A comprehensive backend API for Serri Flow - combining document processing with AI-powered customer support chatbot functionality.

## Features

### Document Bot (ML Assignment)
- **Document Processing**: Upload and process PDF/TXT documents
- **Text Extraction**: Extract and split text into manageable sections
- **Semantic Search**: Create embeddings using sentence-transformers for semantic search
- **QA Pipeline**: Answer queries using Hugging Face QA pipeline (distilbert-base-uncased-distilled-squad)
- **Feedback Loop**: Handle feedback ("Not Helpful", "Too Vague", "Good") and improve responses
- **Activity Logging**: Comprehensive logging of all actions (document loaded, query asked, feedback, retries)

### Serri AI Interactive Landing Page Backend
- **Lead Qualification**: Chatbot endpoints for lead qualification (industry, company size, decision-making power, interest level)
- **Demo Scheduling**: Integration with Calendly API for demo scheduling
- **Objection Handling**: Pre-defined responses for common objections
- **Follow-up Logic**: Automated reminders if users don't schedule demos
- **Lead Capture**: Secure API for storing leads in PostgreSQL

## Tech Stack

- **Language**: Python 3.8+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **AI/ML**: 
  - Hugging Face Transformers
  - sentence-transformers
  - PyTorch
- **Authentication**: API Key based
- **Document Processing**: PyPDF2
- **Async HTTP**: httpx (for Calendly integration)

## Installation

### Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd serri-flow-ui/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@localhost:5432/serri_flow_db
   
   # API Keys
   API_KEY=your-secret-api-key-here
   CALENDLY_API_TOKEN=your-calendly-token-here
   
   # Hugging Face
   HUGGINGFACE_API_TOKEN=your-huggingface-token-here
   
   # App Settings
   DEBUG=True
   LOG_LEVEL=INFO
   ```

5. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb serri_flow_db
   
   # Run seed script to create tables and sample data
   python scripts/seed_data.py
   ```

6. **Start the server**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Document Bot APIs

#### Upload Document
```http
POST /api/document-bot/upload-doc
Content-Type: multipart/form-data

file: [PDF or TXT file]
```

#### Ask Query
```http
POST /api/document-bot/ask-query
Content-Type: application/json

{
  "doc_id": 1,
  "query": "What is the main topic of this document?"
}
```

#### Submit Feedback
```http
POST /api/document-bot/feedback
Content-Type: application/json

{
  "query_id": 1,
  "feedback": "good"  // "good", "not_helpful", "too_vague"
}
```

#### Get Document Logs
```http
GET /api/document-bot/logs/{doc_id}
```

### Serri Chatbot APIs

#### Chat
```http
POST /api/chatbot/chat
Content-Type: application/json

{
  "message": "Hello, I'm interested in your AI solution",
  "lead_id": 1  // optional
}
```

#### Create Lead
```http
POST /api/chatbot/lead
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "company": "TechCorp",
  "industry": "tech",
  "company_size": "51-200",
  "role": "CTO",
  "decision_making_power": "high",
  "interest_level": "high"
}
```

#### Schedule Demo
```http
POST /api/chatbot/schedule-demo
Content-Type: application/json

{
  "lead_id": 1,
  "preferred_date": "2024-01-15T10:00:00Z",
  "timezone": "UTC"
}
```

#### Handle Objection
```http
POST /api/chatbot/objection
Content-Type: application/json

{
  "objection_type": "price",
  "lead_id": 1,
  "context": "It's too expensive for our budget"
}
```

#### Send Follow-up
```http
POST /api/chatbot/followup
Content-Type: application/json

{
  "lead_id": 1,
  "follow_up_type": "demo_reminder"
}
```

## Authentication

The API uses API key authentication. Include the API key in the Authorization header:

```http
Authorization: Bearer your-api-key-here
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication
│   ├── routers/             # API routes
│   │   ├── document_bot.py  # Document bot endpoints
│   │   └── chatbot.py       # Chatbot endpoints
│   └── services/            # Business logic
│       ├── document_processor.py  # Document processing
│       ├── qa_service.py          # QA pipeline
│       ├── chatbot_service.py     # Chatbot logic
│       ├── objection_handler.py   # Objection handling
│       └── calendly_service.py    # Calendly integration
├── scripts/
│   └── seed_data.py         # Database seeding
├── uploads/                 # Document upload directory
├── requirements.txt         # Python dependencies
├── alembic.ini             # Database migration config
└── README.md               # This file
```

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Adding New Features

1. **Models**: Add new SQLAlchemy models in `app/models.py`
2. **Schemas**: Add Pydantic schemas in `app/schemas.py`
3. **Services**: Add business logic in `app/services/`
4. **Routes**: Add API endpoints in `app/routers/`
5. **Update**: Update this README with new endpoints

## Production Deployment

### Environment Variables
- Set `DEBUG=False`
- Use strong `API_KEY`
- Configure production `DATABASE_URL`
- Set up proper logging

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Considerations
- Use HTTPS in production
- Implement rate limiting
- Add input validation
- Use environment variables for secrets
- Regular security updates

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **Model Loading Error**
   - Check internet connection for Hugging Face models
   - Verify HUGGINGFACE_API_TOKEN if using private models

3. **File Upload Error**
   - Check uploads directory permissions
   - Verify file size limits

4. **Calendly Integration Error**
   - Check CALENDLY_API_TOKEN
   - Verify Calendly API permissions

### Logs
Check application logs for detailed error information:
```bash
tail -f logs/app.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for error details
