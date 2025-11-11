"""
Comprehensive API Testing Suite for FinBuddy
Tests all endpoints and functionality with detailed logging
"""
import requests
import json
import logging
import time
from typing import Dict, Any
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": f"test_user_{int(time.time())}",
    "email": f"test_{int(time.time())}@example.com",
    "password": "Test@123456",
    "risk_tolerance": "medium"
}

class FinBuddyTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.user_id = None
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        logger.info("=" * 80)
        logger.info("🧪 FinBuddy Comprehensive Test Suite")
        logger.info("=" * 80)
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        if success:
            self.test_results["passed"] += 1
            logger.info(f"✅ PASS: {test_name}")
            if details:
                logger.info(f"   📝 {details}")
        else:
            self.test_results["failed"] += 1
            logger.error(f"❌ FAIL: {test_name}")
            if details:
                logger.error(f"   📝 {details}")
            self.test_results["errors"].append({
                "test": test_name,
                "details": details
            })
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None) -> tuple:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            logger.info(f"\n🌐 {method} {url}")
            if data:
                logger.info(f"   📤 Request: {json.dumps(data, indent=2)}")
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            
            logger.info(f"   📥 Status: {response.status_code}")
            
            try:
                response_data = response.json()
                logger.info(f"   📥 Response: {json.dumps(response_data, indent=2)}")
                return response.status_code, response_data
            except:
                logger.info(f"   📥 Response: {response.text}")
                return response.status_code, response.text
                
        except requests.exceptions.ConnectionError:
            logger.error(f"   ❌ Connection Error: Cannot connect to {url}")
            logger.error(f"   💡 Make sure the server is running!")
            return None, {"error": "Connection Error - Server not running"}
        except requests.exceptions.Timeout:
            logger.error(f"   ❌ Timeout Error: Request took too long")
            return None, {"error": "Timeout Error"}
        except Exception as e:
            logger.error(f"   ❌ Error: {str(e)}")
            return None, {"error": str(e)}
    
    def test_1_server_health(self):
        """Test 1: Check if server is running"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: Server Health Check")
        logger.info("=" * 80)
        
        status, data = self.make_request("GET", "/")
        if status == 200:
            self.log_test("Server Health Check", True, f"Server is running: {data.get('version', 'N/A')}")
        else:
            self.log_test("Server Health Check", False, "Server not responding")
            return False
        
        status, data = self.make_request("GET", "/health")
        if status == 200:
            gemini_status = data.get("gemini_configured", False)
            self.log_test("Health Endpoint", True, 
                         f"Gemini: {'✅ Configured' if gemini_status else '❌ Not Configured'}")
        else:
            self.log_test("Health Endpoint", False, "Health check failed")
        
        return True
    
    def test_2_user_registration(self):
        """Test 2: User Registration"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 2: User Registration")
        logger.info("=" * 80)
        
        status, data = self.make_request("POST", "/api/users/register", TEST_USER)
        if status == 201:
            self.user_id = data.get("id")
            self.log_test("User Registration", True, f"User ID: {self.user_id}")
            return True
        else:
            self.log_test("User Registration", False, 
                         f"Status: {status}, Response: {data}")
            return False
    
    def test_3_get_user_profile(self):
        """Test 3: Get User Profile"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 3: Get User Profile")
        logger.info("=" * 80)
        
        if not self.user_id:
            self.log_test("Get User Profile", False, "No user_id available")
            return False
        
        status, data = self.make_request("GET", f"/api/users/{self.user_id}")
        if status == 200:
            self.log_test("Get User Profile", True, 
                         f"Username: {data.get('username', 'N/A')}")
            return True
        else:
            self.log_test("Get User Profile", False, f"Status: {status}")
            return False
    
    def test_4_add_investment(self):
        """Test 4: Add Investment"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 4: Add Investment")
        logger.info("=" * 80)
        
        if not self.user_id:
            self.log_test("Add Investment", False, "No user_id available")
            return False
        
        investment_data = {
            "symbol": "AAPL",
            "asset_type": "stock",
            "quantity": 10.0,
            "purchase_price": 150.0
        }
        
        status, data = self.make_request("POST", 
                                        f"/api/investments/{self.user_id}",
                                        investment_data)
        if status == 201:
            self.log_test("Add Investment", True, 
                         f"Investment ID: {data.get('id', 'N/A')}")
            return True
        else:
            self.log_test("Add Investment", False, f"Status: {status}")
            return False
    
    def test_5_get_portfolio(self):
        """Test 5: Get Portfolio"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 5: Get Portfolio")
        logger.info("=" * 80)
        
        if not self.user_id:
            self.log_test("Get Portfolio", False, "No user_id available")
            return False
        
        status, data = self.make_request("GET", f"/api/portfolio/{self.user_id}")
        if status == 200:
            investments = data.get("investments", [])
            self.log_test("Get Portfolio", True, 
                         f"Found {len(investments)} investment(s)")
            return True
        else:
            self.log_test("Get Portfolio", False, f"Status: {status}")
            return False
    
    def test_6_explain_term(self):
        """Test 6: Explain Financial Term (Gemini API)"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 6: Explain Financial Term (Gemini AI)")
        logger.info("=" * 80)
        
        term_data = {"term": "Dividend"}
        status, data = self.make_request("POST", "/api/ai/explain-term", term_data)
        
        if status == 200:
            explanation = data.get("explanation", "")
            self.log_test("Explain Term (Gemini)", True, 
                         f"Explanation length: {len(explanation)} chars")
            return True
        else:
            self.log_test("Explain Term (Gemini)", False, 
                         f"Status: {status}, Error: {data}")
            return False
    
    def test_7_chat_with_ai(self):
        """Test 7: Chat with AI (Gemini API)"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 7: Chat with AI (Gemini API)")
        logger.info("=" * 80)
        
        chat_data = {
            "message": "What is a good investment strategy for beginners?",
            "user_id": self.user_id
        }
        status, data = self.make_request("POST", "/api/ai/chat", chat_data)
        
        if status == 200:
            response = data.get("response", "")
            self.log_test("Chat with AI (Gemini)", True, 
                         f"Response length: {len(response)} chars")
            return True
        else:
            self.log_test("Chat with AI (Gemini)", False, 
                         f"Status: {status}, Error: {data}")
            return False
    
    def test_8_detect_scam(self):
        """Test 8: Detect Scam (Gemini API)"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 8: Detect Scam (Gemini AI)")
        logger.info("=" * 80)
        
        scam_data = {
            "message": "You've won $1 million! Send us your bank details now!",
            "sender": "unknown@suspicious.com"
        }
        status, data = self.make_request("POST", "/api/fraud/detect-scam", scam_data)
        
        if status == 200:
            is_suspicious = data.get("is_suspicious", False)
            confidence = data.get("confidence", 0)
            self.log_test("Detect Scam (Gemini)", True, 
                         f"Suspicious: {is_suspicious}, Confidence: {confidence}")
            return True
        else:
            self.log_test("Detect Scam (Gemini)", False, 
                         f"Status: {status}, Error: {data}")
            return False
    
    def test_9_check_url(self):
        """Test 9: Check URL Safety"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 9: Check URL Safety")
        logger.info("=" * 80)
        
        url_data = {"url": "http://suspicious-investment.com"}
        status, data = self.make_request("POST", "/api/fraud/check-url", url_data)
        
        if status == 200:
            is_safe = data.get("is_safe", True)
            self.log_test("Check URL", True, 
                         f"Safe: {is_safe}")
            return True
        else:
            self.log_test("Check URL", False, f"Status: {status}")
            return False
    
    def test_10_analyze_portfolio_risk(self):
        """Test 10: Analyze Portfolio Risk"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 10: Analyze Portfolio Risk")
        logger.info("=" * 80)
        
        if not self.user_id:
            self.log_test("Analyze Portfolio Risk", False, "No user_id available")
            return False
        
        status, data = self.make_request("GET", 
                                        f"/api/risk/analyze-portfolio/{self.user_id}")
        if status == 200:
            overall_risk = data.get("overall_risk", "N/A")
            self.log_test("Analyze Portfolio Risk", True, 
                         f"Risk Level: {overall_risk}")
            return True
        else:
            self.log_test("Analyze Portfolio Risk", False, f"Status: {status}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        
        total = self.test_results["passed"] + self.test_results["failed"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        logger.info(f"Total Tests: {total}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        
        if self.test_results["errors"]:
            logger.info("\n" + "=" * 80)
            logger.info("❌ FAILED TESTS DETAILS:")
            logger.info("=" * 80)
            for error in self.test_results["errors"]:
                logger.error(f"\n🔴 {error['test']}")
                logger.error(f"   Details: {error['details']}")
        
        logger.info("\n" + "=" * 80)
        logger.info("🏁 Testing Complete!")
        logger.info("=" * 80)
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        logger.info(f"\n🚀 Starting comprehensive tests at {datetime.now()}")
        logger.info(f"🎯 Target: {self.base_url}\n")
        
        time.sleep(1)
        
        # Run all tests
        if not self.test_1_server_health():
            logger.error("\n⚠️ Server is not running! Please start the server first.")
            logger.error("Run: python run.py")
            self.print_summary()
            return
        
        time.sleep(1)
        self.test_2_user_registration()
        
        time.sleep(1)
        self.test_3_get_user_profile()
        
        time.sleep(1)
        self.test_4_add_investment()
        
        time.sleep(1)
        self.test_5_get_portfolio()
        
        time.sleep(2)  # Extra time for AI calls
        self.test_6_explain_term()
        
        time.sleep(2)
        self.test_7_chat_with_ai()
        
        time.sleep(2)
        self.test_8_detect_scam()
        
        time.sleep(1)
        self.test_9_check_url()
        
        time.sleep(1)
        self.test_10_analyze_portfolio_risk()
        
        # Print summary
        self.print_summary()

if __name__ == "__main__":
    tester = FinBuddyTester()
    tester.run_all_tests()
