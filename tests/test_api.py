"""
Test script for FinBuddy API
Run this after starting the server to test all endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_finbuddy_api():
    """Test all major FinBuddy endpoints"""
    
    print("🚀 Testing FinBuddy API...")
    
    # 1. Health check
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    
    # 2. Register a user
    user_data = {
        "username": "john_investor",
        "email": "john@example.com",
        "password": "securepass123",
        "risk_tolerance": "medium"
    }
    response = requests.post(f"{BASE_URL}/api/users/register", json=user_data)
    print_response("Register User", response)
    
    user_id = response.json().get('id', 1)
    
    # 3. Add an investment
    investment_data = {
        "symbol": "AAPL",
        "asset_type": "stock",
        "quantity": 10,
        "purchase_price": 150.00
    }
    response = requests.post(
        f"{BASE_URL}/api/investments?user_id={user_id}",
        json=investment_data
    )
    print_response("Add Investment", response)
    
    investment_id = response.json().get('investment_id', 1)
    
    # 4. Get risk analysis
    response = requests.get(f"{BASE_URL}/api/investments/{investment_id}/risk-analysis")
    print_response("Risk Analysis", response)
    
    # 5. Chat with AI
    chat_data = {
        "message": "What is a stock market?",
        "user_id": user_id
    }
    response = requests.post(f"{BASE_URL}/api/ai/chat", json=chat_data)
    print_response("AI Chat", response)
    
    # 6. Explain financial term
    term_data = {
        "term": "diversification"
    }
    response = requests.post(f"{BASE_URL}/api/ai/explain-term", json=term_data)
    print_response("Explain Term", response)
    
    # 7. Check for scam
    scam_data = {
        "message": "URGENT! Send $500 now to claim your guaranteed returns of 1000% in 24 hours!",
        "sender": "unknown@scam.com"
    }
    response = requests.post(f"{BASE_URL}/api/security/check-scam", json=scam_data)
    print_response("Scam Detection", response)
    
    # 8. Check URL safety
    url_data = {
        "url": "http://192.168.1.1/secure-login/verify-account"
    }
    response = requests.post(f"{BASE_URL}/api/security/check-url", json=url_data)
    print_response("URL Safety Check", response)
    
    # 9. Get learning module
    response = requests.get(f"{BASE_URL}/api/learning/module/compound interest")
    print_response("Learning Module", response)
    
    # 10. Get dashboard
    response = requests.get(f"{BASE_URL}/api/dashboard/{user_id}")
    print_response("User Dashboard", response)
    
    print(f"\n{'='*60}")
    print("✅ All tests completed!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    try:
        test_finbuddy_api()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure the server is running: python main.py")
    except Exception as e:
        print(f"❌ Error: {e}")
