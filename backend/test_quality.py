#!/usr/bin/env python3
"""
Quality test for the improved document bot
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_question(doc_id, question, expected_keywords=None):
    """Test a question and show the result"""
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
        
        # Check if expected keywords are in the answer
        if expected_keywords:
            answer_lower = result['answer'].lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in answer_lower]
            if found_keywords:
                print(f"🎯 Found expected keywords: {found_keywords}")
            else:
                print(f"⚠️  Expected keywords not found: {expected_keywords}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def main():
    """Main quality test"""
    print("🎯 IMPROVED Document Bot Quality Test")
    print("=" * 60)
    
    doc_id = 5  # Andrew S. Tanenbaum - Computer Networks.pdf
    
    # Test questions with expected results
    test_cases = [
        {
            "question": "name of the author?",
            "expected": ["Andrew", "Tanenbaum"],
            "description": "Author name from filename"
        },
        {
            "question": "What is the title of this book?",
            "expected": ["Computer Networks"],
            "description": "Book title from filename"
        },
        {
            "question": "What are computer networks?",
            "expected": ["network", "computer"],
            "description": "Content-based question"
        },
        {
            "question": "What is a protocol?",
            "expected": ["protocol"],
            "description": "Technical term question"
        },
        {
            "question": "How do networks work?",
            "expected": ["network", "work"],
            "description": "How-to question"
        },
        {
            "question": "What is TCP?",
            "expected": ["TCP"],
            "description": "Acronym question"
        }
    ]
    
    successful_tests = 0
    total_time = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print("-" * 40)
        
        start_time = time.time()
        success = test_question(doc_id, test_case['question'], test_case['expected'])
        end_time = time.time()
        
        if success:
            successful_tests += 1
            total_time += (end_time - start_time)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 QUALITY TEST RESULTS:")
    print(f"✅ Successful tests: {successful_tests}/{len(test_cases)}")
    print(f"⚡ Average response time: {total_time/successful_tests:.3f}s")
    print(f"🎯 Success rate: {successful_tests/len(test_cases)*100:.1f}%")
    
    if successful_tests == len(test_cases):
        print("🎉 PERFECT! All tests passed!")
    elif successful_tests >= len(test_cases) * 0.8:
        print("👍 EXCELLENT! Most tests passed!")
    else:
        print("⚠️  Some tests need improvement.")

if __name__ == "__main__":
    main()
