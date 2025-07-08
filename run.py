#!/usr/bin/env python3
"""
Question Paper Generator - Run Script
Simple script to start the application with proper configuration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'openai', 'PyPDF2', 'python-docx', 
        'openpyxl', 'Pillow', 'pytesseract', 'pandas', 'numpy'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_openai_key():
    """Check if OpenAI API key is configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("❌ OpenAI API key not configured!")
        print("📝 Please:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenAI API key to the .env file")
        print("   3. Get your API key from: https://platform.openai.com/api-keys")
        return False
    
    return True

def check_tesseract():
    """Check if Tesseract OCR is installed"""
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        print("⚠️  Tesseract OCR not found!")
        print("📝 Install Tesseract OCR:")
        print("   - Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("   - macOS: brew install tesseract")
        print("   - Windows: Download from GitHub releases")
        print("   Note: OCR functionality will be limited without Tesseract")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['static', 'models', 'services']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Main function to run the application"""
    print("🚀 Starting Question Paper Generator...")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check OpenAI API key
    if not check_openai_key():
        sys.exit(1)
    
    # Check Tesseract (warning only)
    tesseract_available = check_tesseract()
    
    # Create directories
    create_directories()
    
    # Get configuration
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    
    print("✅ All dependencies checked!")
    if tesseract_available:
        print("✅ Tesseract OCR available!")
    print("✅ OpenAI API key configured!")
    print("=" * 50)
    print(f"🌐 Starting server at http://{host}:{port}")
    print("📖 Check the README.md for usage instructions")
    print("❌ Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the application
    try:
        import uvicorn
        from main import app
        
        uvicorn.run(
            app, 
            host=host, 
            port=port,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()