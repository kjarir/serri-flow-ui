#!/bin/bash

# Serri Flow Backend Setup Script

echo "🚀 Setting up Serri Flow Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. Please install PostgreSQL and create a database."
    echo "   You can install it with: brew install postgresql (macOS) or apt-get install postgresql (Ubuntu)"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "⚙️  Creating .env file..."
    cp env.example .env
    echo "📝 Please edit .env file with your database and API credentials"
fi

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database URL and API keys"
echo "2. Create PostgreSQL database: createdb serri_flow_db"
echo "3. Run seed script: python scripts/seed_data.py"
echo "4. Start the server: python run.py"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
