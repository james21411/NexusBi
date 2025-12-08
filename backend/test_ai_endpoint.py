#!/usr/bin/env python3
"""
Test script to verify AI endpoint functionality
Run this script to test if the AI endpoint is working correctly
"""

import requests
import json
from time import sleep

def test_backend_health():
    """Test if backend is running and healthy"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get("http://127.0.0.1:8000/health")
        if response.status_code == 200:
            print("✅ Backend is healthy:", response.json())
            return True
        else:
            print("❌ Backend health check failed:", response.status_code)
            return False
    except Exception as e:
        print("❌ Cannot connect to backend:", str(e))
        return False

def test_ai_endpoint():
    """Test the AI query endpoint"""
    print("\n🔍 Testing AI endpoint...")
    try:
        # Test data
        test_query = {
            "query": "Bonjour, comment ça va aujourd'hui?",
            "model": "gemini-pro",
            "temperature": 0.7,
            "max_tokens": 1024
        }

        response = requests.post(
            "http://127.0.0.1:8000/api/v1/ai/query",
            json=test_query,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print("✅ AI endpoint works!")
            print("📝 Response:", result.get("response", "No response")[:100] + "...")
            print("🔧 Model used:", result.get("model_used", "Unknown"))
            print("💬 Tokens used:", result.get("tokens_used", 0))
            return True
        else:
            print("❌ AI endpoint failed with status:", response.status_code)
            print("📋 Response:", response.text)
            return False
    except Exception as e:
        print("❌ Cannot connect to AI endpoint:", str(e))
        return False

def test_cors_headers():
    """Test CORS headers"""
    print("\n🔍 Testing CORS headers...")
    try:
        response = requests.options(
            "http://127.0.0.1:8000/api/v1/ai/query",
            headers={"Origin": "http://localhost:5173"}  # Typical frontend port
        )

        cors_headers = response.headers.get('access-control-allow-origin', '')
        if cors_headers:
            print("✅ CORS is enabled:", cors_headers)
            return True
        else:
            print("❌ CORS headers not found")
            return False
    except Exception as e:
        print("❌ Cannot test CORS:", str(e))
        return False

def main():
    """Run all tests"""
    print("🚀 Starting AI endpoint test suite...")
    print("=" * 50)

    # Wait a moment for backend to start if needed
    sleep(1)

    tests = [
        ("Backend Health", test_backend_health),
        ("AI Endpoint", test_ai_endpoint),
        ("CORS Headers", test_cors_headers),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("=" * 50)

    all_passed = True
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if not result:
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("🎉 All tests passed! The AI endpoint is working correctly.")
        print("\n💡 Next steps:")
        print("1. Make sure frontend is running on the correct port")
        print("2. Check that API_BASE_URL in frontend matches backend URL")
        print("3. Verify that GEMINI_API_KEY is configured in backend .env file")
    else:
        print("❌ Some tests failed. Check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("1. Is backend running? (python -m uvicorn main:app --reload)")
        print("2. Is the correct port being used? (8000)")
        print("3. Are there any firewall/port conflicts?")
        print("4. Check backend logs for errors")

if __name__ == "__main__":
    main()
