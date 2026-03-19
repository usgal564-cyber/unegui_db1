#!/usr/bin/env python3
"""
Setup script for the advertisement website
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is 3.8 or higher"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✓ Python version: {sys.version}")

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file with default settings"""
    env_content = """# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/unegui_db

# Upload Configuration
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ .env file created!")
        print("Please update the DATABASE_URL in .env file with your PostgreSQL credentials.")
    else:
        print("✓ .env file already exists!")

def main():
    """Main setup function"""
    print("=== Зарын Сайт Setup ===")
    print()
    
    check_python_version()
    install_requirements()
    create_env_file()
    
    print()
    print("=== Setup Complete! ===")
    print()
    print("Next steps:")
    print("1. Install PostgreSQL and create database 'unegui_db'")
    print("2. Update DATABASE_URL in .env file")
    print("3. Run: python init_db.py")
    print("4. Run: python app.py")
    print("5. Open: http://localhost:5000")
    print()
    print("Default admin login:")
    print("Email: admin@zariin-sait.mn")
    print("Password: admin123")
    print()

if __name__ == '__main__':
    main()
