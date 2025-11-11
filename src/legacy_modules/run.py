"""
Quick Setup and Run Script for FinBuddy
This script will help you set up and run FinBuddy quickly
"""
import os
import subprocess
import sys

def print_banner():
    print("=" * 60)
    print("🤖 FinBuddy - AI-Powered Financial Companion")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  .env file not found. Creating from template...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as src:
                content = src.read()
            with open('.env', 'w') as dst:
                dst.write(content)
            print("✅ Created .env file")
            print("⚠️  IMPORTANT: Edit .env and add your GEMINI_API_KEY")
            print("   Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        else:
            print("❌ .env.example not found")
            return False
    
    # Check if API key is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content or 'GEMINI_API_KEY=' == content.split('\n')[0].strip():
            print("⚠️  GEMINI_API_KEY not configured in .env file")
            print("   Please edit .env and add your actual API key")
            return False
    
    print("✅ .env file configured")
    return True

def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def run_server():
    """Run the FastAPI server"""
    print("\n🚀 Starting FinBuddy server...")
    print("   Server will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("\n   Press Ctrl+C to stop the server\n")
    
    try:
        import uvicorn
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n\n👋 FinBuddy server stopped")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")

def main():
    print_banner()
    
    if not check_python_version():
        sys.exit(1)
    
    env_ok = check_env_file()
    
    if not env_ok:
        print("\n" + "=" * 60)
        print("⚠️  Setup incomplete. Please configure your .env file first.")
        print("=" * 60)
        response = input("\nDo you want to continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("\n👋 Setup cancelled. Configure .env and run this script again.")
            sys.exit(0)
    
    if not install_dependencies():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("=" * 60)
    
    run_server()

if __name__ == "__main__":
    main()
