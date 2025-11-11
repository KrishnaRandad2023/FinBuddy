"""
Quick Test Script - Verify All Services Work
Tests all microservices are running and responsive
"""
import requests
import time
import sys

SERVICES = {
    "API Gateway": "http://localhost:8000",
    "User Service": "http://localhost:8001",
    "Portfolio Service": "http://localhost:8002",
    "News Service": "http://localhost:8003",
    "AI Service": "http://localhost:8004",
    "Risk Service": "http://localhost:8005",
    "Learning Service": "http://localhost:8006"
}

def test_service(name, url):
    """Test if a service is running"""
    try:
        response = requests.get(f"{url}/health", timeout=3)
        if response.status_code == 200:
            print(f"✅ {name:<20} - HEALTHY")
            return True
        else:
            print(f"⚠️  {name:<20} - UNHEALTHY (Status: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name:<20} - NOT RUNNING")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️  {name:<20} - TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {name:<20} - ERROR: {str(e)}")
        return False

def main():
    print("")
    print("=" * 60)
    print("  🧪 FinBuddy Microservices Health Check")
    print("=" * 60)
    print("")
    print("Testing all services...")
    print("")
    
    results = {}
    for name, url in SERVICES.items():
        results[name] = test_service(name, url)
        time.sleep(0.5)
    
    print("")
    print("=" * 60)
    
    total = len(results)
    healthy = sum(1 for v in results.values() if v)
    
    if healthy == total:
        print(f"✅ ALL SERVICES HEALTHY ({healthy}/{total})")
        print("=" * 60)
        print("")
        print("🎉 Your microservices architecture is working perfectly!")
        print("")
        print("📖 View API Documentation:")
        print("   http://localhost:8000/docs")
        print("")
        print("🌐 Access API Gateway:")
        print("   http://localhost:8000")
        print("")
        sys.exit(0)
    else:
        print(f"⚠️  SOME SERVICES DOWN ({healthy}/{total} healthy)")
        print("=" * 60)
        print("")
        print("💡 To start all services:")
        print("   .\\scripts\\start_all_services.ps1")
        print("")
        sys.exit(1)

if __name__ == "__main__":
    main()
