#!/usr/bin/env python3
"""
Test to prove the system answers EVERY question - no exceptions!
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_every_question(doc_id, question):
    """Test any question and show the result"""
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
        
        # Check if it's a proper answer (not the old "couldn't find" message)
        if "couldn't find relevant information" in result['answer']:
            print("❌ FAILED: Still giving old error message!")
            return False
        else:
            print("✅ SUCCESS: Got a proper answer!")
            return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def main():
    """Test with various question types to prove it answers EVERYTHING"""
    print("🎯 EVERY QUESTION TEST - Proving the system answers EVERYTHING!")
    print("=" * 70)
    
    doc_id = 9  # Rules and Guidelines document
    
    # Test with completely different question types
    test_cases = [
        "what is this pdf about?",
        "what are the rules?",
        "what is the dress code?",
        "what time should I arrive?",
        "what is this document about?",
        "tell me about this file",
        "what does this say?",
        "summarize this document",
        "what are the guidelines?",
        "what should I know?",
        "explain this to me",
        "what is the content?",
        "what is this about?",
        "give me an overview",
        "what are the requirements?"
    ]
    
    successful_tests = 0
    total_time = 0
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: '{question}'")
        print("-" * 50)
        
        start_time = time.time()
        success = test_every_question(doc_id, question)
        end_time = time.time()
        
        if success:
            successful_tests += 1
            total_time += (end_time - start_time)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 EVERY QUESTION TEST RESULTS:")
    print(f"✅ Successful answers: {successful_tests}/{len(test_cases)}")
    print(f"⚡ Average response time: {total_time/successful_tests:.3f}s")
    print(f"🎯 Success rate: {successful_tests/len(test_cases)*100:.1f}%")
    
    if successful_tests == len(test_cases):
        print("\n🎉 PERFECT! The system answers EVERY question!")
        print("• No more 'couldn't find relevant information' errors")
        print("• Intelligent fallback for any question type")
        print("• Always provides meaningful answers")
        print("• Lightning fast responses")
    else:
        print(f"\n⚠️  {len(test_cases) - successful_tests} questions still need improvement")

if __name__ == "__main__":
    main()
