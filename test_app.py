#!/usr/bin/env python3
"""
Test script for the advertisement website
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Advertisement
from werkzeug.security import generate_password_hash

def test_database_connection():
    """Test database connection"""
    try:
        with app.app_context():
            db.create_all()
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_user_creation():
    """Test user creation"""
    try:
        with app.app_context():
            # Check if test user exists
            test_user = User.query.filter_by(email='test@example.com').first()
            if test_user:
                print("✓ Test user already exists!")
                return True
            
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('test123'),
                phone='9999-9999'
            )
            db.session.add(test_user)
            db.session.commit()
            print("✓ Test user created successfully!")
            return True
    except Exception as e:
        print(f"✗ User creation failed: {e}")
        return False

def test_advertisement_creation():
    """Test advertisement creation"""
    try:
        with app.app_context():
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                print("✗ No user found for ad creation test")
                return False
            
            # Create test advertisement
            test_ad = Advertisement(
                title='Test Advertisement',
                category='үл хөдлөх',
                description='This is a test advertisement',
                price=100000,
                phone='9999-9999',
                user_id=user.id
            )
            db.session.add(test_ad)
            db.session.commit()
            print("✓ Test advertisement created successfully!")
            return True
    except Exception as e:
        print(f"✗ Advertisement creation failed: {e}")
        return False

def test_routes():
    """Test basic routes"""
    try:
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            if response.status_code == 200:
                print("✓ Home page route works!")
            else:
                print(f"✗ Home page failed: {response.status_code}")
                return False
            
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                print("✓ Login page route works!")
            else:
                print(f"✗ Login page failed: {response.status_code}")
                return False
            
            # Test register page
            response = client.get('/register')
            if response.status_code == 200:
                print("✓ Register page route works!")
            else:
                print(f"✗ Register page failed: {response.status_code}")
                return False
            
            return True
    except Exception as e:
        print(f"✗ Route testing failed: {e}")
        return False

def cleanup_test_data():
    """Clean up test data"""
    try:
        with app.app_context():
            # Delete test advertisements
            Advertisement.query.filter_by(title='Test Advertisement').delete()
            
            # Delete test user
            User.query.filter_by(email='test@example.com').delete()
            
            db.session.commit()
            print("✓ Test data cleaned up!")
            return True
    except Exception as e:
        print(f"✗ Cleanup failed: {e}")
        return False

def main():
    """Main test function"""
    print("=== Testing Advertisement Website ===")
    print()
    
    tests = [
        ("Database Connection", test_database_connection),
        ("User Creation", test_user_creation),
        ("Advertisement Creation", test_advertisement_creation),
        ("Basic Routes", test_routes),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print("=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The application is ready to use.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
    
    # Clean up test data
    print("\nCleaning up test data...")
    cleanup_test_data()
    
    print("\n=== Test Complete ===")

if __name__ == '__main__':
    main()
