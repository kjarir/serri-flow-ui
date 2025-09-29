#!/usr/bin/env python3
"""
Speed test for the fast document bot
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_query_speed(doc_id, question):
    """Test the speed of a single query"""
    start_time = time.time()
    
    data = {"doc_id": doc_id, "query": question}
    response = requests.post(f"{API_BASE}/api/document-bot/ask-query", json=data, headers=HEADERS)
    
    end_time = time.time()
    response_time = end_time - start_time
    
    if response.status_code == 200:
        result = response.json()
        return {
            "success": True,
            "response_time": response_time,
            "answer": result['answer'],
            "confidence": result['confidence_score']
        }
    else:
        return {
            "success": False,
            "response_time": response_time,
            "error": response.text
        }

def main():
    """Main speed test"""
    print("🚀 FAST Document Bot Speed Test")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What is Serri AI?",
        "What are the pricing plans?",
        "What file formats are supported?",
        "Is there a free trial?",
        "How accurate are the AI responses?",
        "What are the technical requirements?",
        "Can I integrate with my existing CRM?",
        "What are the key features?"
    ]
    
    doc_id = 4  # Use the uploaded document
    
    total_time = 0
    successful_queries = 0
    
    print(f"Testing {len(test_queries)} queries...")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Query: '{query}'")
        result = test_query_speed(doc_id, query)
        
        if result["success"]:
            print(f"   ✅ Response time: {result['response_time']:.3f}s")
            print(f"   📊 Confidence: {result['confidence']:.2f}")
            print(f"   💬 Answer: {result['answer'][:100]}...")
            total_time += result['response_time']
            successful_queries += 1
        else:
            print(f"   ❌ Failed: {result['error']}")
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 SPEED TEST RESULTS:")
    print(f"✅ Successful queries: {successful_queries}/{len(test_queries)}")
    print(f"⚡ Average response time: {total_time/successful_queries:.3f}s")
    print(f"🏃 Total time for all queries: {total_time:.3f}s")
    print(f"🚀 Queries per second: {successful_queries/total_time:.1f}")
    
    if total_time/successful_queries < 0.1:
        print("🎉 EXCELLENT! Response times are under 100ms!")
    elif total_time/successful_queries < 0.5:
        print("👍 GOOD! Response times are under 500ms!")
    else:
        print("⚠️  Response times could be improved.")

if __name__ == "__main__":
    main()
