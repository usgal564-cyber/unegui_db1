#!/usr/bin/env python3
"""
Database initialization script for the advertisement website
"""

from app import app, db, User, Advertisement, RealEstate, Automobile, Job, AdvertisementImage
from werkzeug.security import generate_password_hash
import os

def init_database():
    """Initialize the database with tables and sample data"""
    
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("Tables created successfully!")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(email='admin@zariin-sait.mn').first()
        if not admin_user:
            # Create admin user
            print("Creating admin user...")
            admin_user = User(
                username='admin',
                email='admin@zariin-sait.mn',
                password_hash=generate_password_hash('admin123'),
                phone='9999-9999'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created!")
        else:
            print("Admin user already exists!")
        
        # Create sample advertisements
        create_sample_ads()
        
        print("Database initialization completed!")

def create_sample_ads():
    """Create sample advertisements for testing"""
    
    # Check if sample ads already exist
    if Advertisement.query.count() > 0:
        print("Sample advertisements already exist!")
        return
    
    print("Creating sample advertisements...")
    
    # Get admin user
    admin_user = User.query.filter_by(email='admin@zariin-sait.mn').first()
    
    # Sample Real Estate Ad
    real_estate_ad = Advertisement(
        title='3 өрөө байр зарна',
        category='үл хөдлөх',
        description='Хан-Уул дүүрэгт байрлах шинэ 3 өрөө байр зарна. Бүх орчин тав тухтай, цэвэрхэн.',
        price=120000000,
        phone='8888-8888',
        user_id=admin_user.id
    )
    db.session.add(real_estate_ad)
    db.session.flush()
    
    real_estate = RealEstate(
        advertisement_id=real_estate_ad.id,
        area=85.5,
        location='Хан-Уул дүүрэг, 15-р хороо',
        rooms=3,
        floor=5,
        garage=True,
        condition='шинэ',
        year_built=2023
    )
    db.session.add(real_estate)
    
    # Sample Automobile Ad
    automobile_ad = Advertisement(
        title='Toyota Camry 2020',
        category='автомашин',
        description='Машин сайн төлөвтэй, ойролцоогоор 40,000 км явсан. ГААТАас шалгагдсан.',
        price=55000000,
        phone='7777-7777',
        user_id=admin_user.id
    )
    db.session.add(automobile_ad)
    db.session.flush()
    
    automobile = Automobile(
        advertisement_id=automobile_ad.id,
        manufacturer='Toyota',
        model='Camry',
        year=2020,
        type='жижиг',
        engine_capacity=2.5,
        drive_type='урагшаа',
        transmission='автомат',
        fuel_type='бензин',
        doors=4,
        mileage=40000,
        has_plate=True
    )
    db.session.add(automobile)
    
    # Sample Job Ad
    job_ad = Advertisement(
        title='Web Developer ажилд авна',
        category='ажил',
        description='Манай компанид веб хөгжүүлэгч ажилд авна. Flask, Django туршлагатай.',
        price=5000000,
        phone='9999-9999',
        user_id=admin_user.id
    )
    db.session.add(job_ad)
    db.session.flush()
    
    job = Job(
        advertisement_id=job_ad.id,
        sector='IT',
        sub_sector='Хөгжүүлэлт',
        position='Senior Web Developer',
        salary=5000000,
        requirements='Python, Flask, Django, PostgreSQL, HTML, CSS, JavaScript',
        degree='бакалавр',
        experience='3-5 жил',
        location='Улаанбаатар'
    )
    db.session.add(job)
    
    db.session.commit()
    print("Sample advertisements created!")

def reset_database():
    """Reset the database (drop all tables and recreate)"""
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Tables dropped!")
        
        init_database()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'reset':
        reset_database()
    else:
        init_database()
