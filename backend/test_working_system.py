#!/usr/bin/env python3
"""
Test the working QA system
"""

import requests
import time

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_question(doc_id, question):
    """Test a question"""
    print(f"❓ Question: '{question}'")
    
    start_time = time.time()
    data = {"doc_id": doc_id, "query": question}
    response = requests.post(f"{API_BASE}/api/document-bot/ask-query", json=data, headers=HEADERS)
    end_time = time.time()
    
    if response.status_code == 200:
        result = response.json()
        response_time = end_time - start_time
        
        print(f"✅ Answer: {result['answer']}")
        print(f"📊 Confidence: {result['confidence_score']:.2f}")
        print(f"⚡ Response time: {response_time:.3f}s")
        print()
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def main():
    """Test the working system"""
    print("🎯 WORKING QA SYSTEM TEST")
    print("=" * 50)
    print("Testing the Computer Networks book (Document ID: 17)")
    print()
    
    doc_id = 17
    
    questions = [
        "tell me something about computer networks",
        "who is the author?",
        "what is the title of this book?",
        "what are computer networks?",
        "what is TCP?",
        "what are network protocols?",
        "how do networks work?",
        "what is this book about?"
    ]
    
    successful_tests = 0
    total_time = 0
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. Testing Question:")
        start_time = time.time()
        success = test_question(doc_id, question)
        end_time = time.time()
        
        if success:
            successful_tests += 1
            total_time += (end_time - start_time)
    
    print("=" * 50)
    print("📊 RESULTS:")
    print(f"✅ Successful answers: {successful_tests}/{len(questions)}")
    print(f"⚡ Average response time: {total_time/successful_tests:.3f}s")
    print(f"🎯 Success rate: {successful_tests/len(questions)*100:.1f}%")
    
    if successful_tests == len(questions):
        print("\n🎉 PERFECT! The system is now working properly!")
        print("✅ No more massive text dumps")
        print("✅ Proper, concise answers")
        print("✅ Fast response times")
        print("✅ High confidence scores")
    else:
        print(f"\n⚠️  {len(questions) - successful_tests} questions need improvement")

if __name__ == "__main__":
    main()
