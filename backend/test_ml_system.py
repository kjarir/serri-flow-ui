#!/usr/bin/env python3
"""
Test the ML-based document processing and QA system
"""

import requests
import time
import json

API_BASE = "http://localhost:8000"
API_KEY = "your-secret-api-key-here"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

def test_ml_question(doc_id, question, expected_keywords=None):
    """Test a question with the ML system"""
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
                return True
            else:
                print(f"⚠️  Expected keywords not found: {expected_keywords}")
                return False
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def main():
    """Test the ML-based system"""
    print("🤖 ML-BASED DOCUMENT PROCESSING & QA SYSTEM TEST")
    print("=" * 70)
    
    doc_id = 15  # Serri AI document processed with ML
    
    print("\n📋 SYSTEM FEATURES:")
    print("• PyMuPDF for advanced PDF processing")
    print("• Intelligent chunking with ML")
    print("• TF-IDF vectorization for similarity matching")
    print("• Pattern-based extraction for specific questions")
    print("• ML-trained keyword matching")
    print("• Cosine similarity for relevance scoring")
    
    print("\n🎯 TESTING ML SYSTEM:")
    print("=" * 50)
    
    # Test various question types
    test_cases = [
        {
            "question": "what is Serri AI?",
            "expected": ["Serri AI", "customer support", "automation"],
            "description": "General Overview Question"
        },
        {
            "question": "what is the pricing?",
            "expected": ["$99", "pricing", "month"],
            "description": "Specific Information Extraction"
        },
        {
            "question": "what are the key features?",
            "expected": ["features", "document processing", "AI"],
            "description": "Feature-based Question"
        },
        {
            "question": "how does it work?",
            "expected": ["work", "process", "AI"],
            "description": "Process Question"
        },
        {
            "question": "what file formats are supported?",
            "expected": ["PDF", "TXT", "formats"],
            "description": "Technical Specification Question"
        },
        {
            "question": "tell me about the platform",
            "expected": ["platform", "Serri AI", "automation"],
            "description": "General Description Question"
        }
    ]
    
    successful_tests = 0
    total_time = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print("-" * 40)
        
        start_time = time.time()
        success = test_ml_question(doc_id, test_case['question'], test_case['expected'])
        end_time = time.time()
        
        if success:
            successful_tests += 1
            total_time += (end_time - start_time)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ML SYSTEM TEST RESULTS:")
    print(f"✅ Successful answers: {successful_tests}/{len(test_cases)}")
    print(f"⚡ Average response time: {total_time/successful_tests:.3f}s")
    print(f"🎯 Success rate: {successful_tests/len(test_cases)*100:.1f}%")
    
    print("\n🤖 ML SYSTEM CAPABILITIES:")
    print("• Advanced PDF processing with PyMuPDF")
    print("• Intelligent document chunking")
    print("• ML-based similarity matching")
    print("• Pattern recognition for specific data")
    print("• TF-IDF vectorization for relevance")
    print("• Cosine similarity scoring")
    print("• Trained keyword extraction")
    
    if successful_tests == len(test_cases):
        print("\n🎉 PERFECT! ML system is working flawlessly!")
    elif successful_tests >= len(test_cases) * 0.8:
        print("\n👍 EXCELLENT! ML system is performing very well!")
    else:
        print("\n⚠️  ML system needs some improvements.")

if __name__ == "__main__":
    main()
