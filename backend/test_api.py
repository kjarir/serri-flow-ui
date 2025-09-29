#!/usr/bin/env python3
"""
Test script to demonstrate the document bot functionality
"""

import requests
import json

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_document_upload():
    """Test document upload"""
    print("📄 Testing document upload...")
    
    with open("test_document.txt", "rb") as f:
        files = {"file": f}
        response = requests.post(f"{API_BASE}/api/document-bot/upload-doc", files=files, headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Document uploaded successfully: {data['filename']} (ID: {data['doc_id']})")
        return data['doc_id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def test_query(doc_id, question):
    """Test query functionality"""
    print(f"❓ Testing query: '{question}'")
    
    data = {"doc_id": doc_id, "query": question}
    response = requests.post(f"{API_BASE}/api/document-bot/ask-query", json=data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Answer: {result['answer']}")
        print(f"📊 Confidence: {result['confidence_score']:.2f}")
        return result
    else:
        print(f"❌ Query failed: {response.text}")
        return None

def test_feedback(query_id, feedback):
    """Test feedback functionality"""
    print(f"💬 Testing feedback: '{feedback}'")
    
    data = {"query_id": query_id, "feedback": feedback}
    response = requests.post(f"{API_BASE}/api/document-bot/feedback", json=data, headers=HEADERS)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Feedback submitted: {result['message']}")
        return result
    else:
        print(f"❌ Feedback failed: {response.text}")
        return None

def main():
    """Main test function"""
    print("🚀 Testing Serri Flow Document Bot API")
    print("=" * 50)
    
    # Test health check
    print("🏥 Testing health check...")
    response = requests.get(f"{API_BASE}/health")
    if response.status_code == 200:
        print("✅ Backend is healthy")
    else:
        print("❌ Backend is not responding")
        return
    
    # Test document upload
    doc_id = test_document_upload()
    if not doc_id:
        return
    
    print("\n" + "=" * 50)
    
    # Test various queries
    test_queries = [
        "What is Serri AI?",
        "What are the pricing plans?",
        "What file formats are supported?",
        "Is there a free trial?",
        "How accurate are the AI responses?",
        "What are the technical requirements?"
    ]
    
    query_results = []
    for query in test_queries:
        result = test_query(doc_id, query)
        if result:
            query_results.append((result, query))
        print()
    
    print("=" * 50)
    
    # Test feedback
    if query_results:
        first_query = query_results[0][0]
        test_feedback(first_query.get('query_id', 1), "good")
        print()
    
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main()
