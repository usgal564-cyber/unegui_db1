from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, IntegerField, TextAreaField, SelectField, FileField, BooleanField, DecimalField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from functools import wraps
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///unegui.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Custom filter for nl2br
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Convert newlines to <br> tags"""
    if text is None:
        return ''
    return re.sub(r'\r?\n', '<br>', str(text))

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    advertisements = db.relationship('Advertisement', backref='user', lazy=True)

class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # 'үл хөдлөх', 'автомашин', 'ажил'
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(15, 2))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    images = db.relationship('AdvertisementImage', backref='advertisement', lazy=True, cascade='all, delete-orphan')
    real_estate = db.relationship('RealEstate', backref='advertisement', uselist=False, cascade='all, delete-orphan')
    automobile = db.relationship('Automobile', backref='advertisement', uselist=False, cascade='all, delete-orphan')
    job = db.relationship('Job', backref='advertisement', uselist=False, cascade='all, delete-orphan')

class AdvertisementImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    is_main = db.Column(db.Boolean, default=False)

class RealEstate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'), nullable=False)
    area = db.Column(db.Numeric(10, 2))  # Талбай
    location = db.Column(db.String(200))  # Байршил
    rooms = db.Column(db.Integer)  # Өрөө
    floor = db.Column(db.Integer)  # Давхар
    garage = db.Column(db.Boolean, default=False)  # Гарааш
    condition = db.Column(db.String(20))  # Шинэ/Хуучин
    year_built = db.Column(db.Integer)  # Он

class Automobile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'), nullable=False)
    manufacturer = db.Column(db.String(100))  # Үйлдвэрлэгч
    model = db.Column(db.String(100))  # Загвар
    year = db.Column(db.Integer)  # Он
    type = db.Column(db.String(50))  # Төрөл (жижиг, жийп)
    engine_capacity = db.Column(db.Numeric(5, 1))  # Моторын багтаамж
    drive_type = db.Column(db.String(50))  # Хөтлөгч
    transmission = db.Column(db.String(50))  # Хүрдний байрлал
    fuel_type = db.Column(db.String(50))  # Түлшний төрөл
    doors = db.Column(db.Integer)  # Хаалганы тоо
    mileage = db.Column(db.Numeric(10, 0))  # Гүйлт
    has_plate = db.Column(db.Boolean, default=False)  # Дугаартай эсэх

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'), nullable=False)
    sector = db.Column(db.String(100))  # Салбар
    sub_sector = db.Column(db.String(100))  # Дэд салбар
    position = db.Column(db.String(200))  # Нэр
    salary = db.Column(db.Numeric(10, 0))  # Цалин
    requirements = db.Column(db.Text)  # Тавигдах шаардлага
    degree = db.Column(db.String(100))  # Зэрэг
    experience = db.Column(db.String(100))  # Туршлага
    location = db.Column(db.String(200))  # Байршил

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Амжилттай нэвтэрлээ!', 'success')
            return redirect(url_for('index'))
        else:
            flash('И-мэйл эсвэл нууц үг буруу байна!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if password != confirm_password:
            flash('Нууц үгүүд таарахгүй байна!', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('Энэ и-мэйл хаягаар бүртгэлтэй байна!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Энэ хэрэглэгчийн нэрээр бүртгэлтэй байна!', 'error')
            return render_template('register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Амжилттай бүртгүүллээ! Та нэвтрэх боломжтой.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Амжилттай гарлаа!', 'success')
    return redirect(url_for('index'))

@app.route('/category/<category>')
def category(category):
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    ads = Advertisement.query.filter_by(category=category, is_active=True)\
                           .order_by(Advertisement.created_at.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('category.html', category=category, ads=ads)

@app.route('/ad/<int:ad_id>')
def ad_detail(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    if not ad.is_active:
        flash('Энэ зар идэвхгүй байна!', 'error')
        return redirect(url_for('index'))
    
    return render_template('ad_detail.html', ad=ad)

@app.route('/post_ad', methods=['GET', 'POST'])
@login_required
def post_ad():
    if request.method == 'POST':
        category = request.form.get('category')
        title = request.form.get('title')
        description = request.form.get('description')
        price = request.form.get('price')
        phone = request.form.get('phone')
        
        # Create advertisement
        new_ad = Advertisement(
            title=title,
            category=category,
            description=description,
            price=float(price) if price else None,
            phone=phone,
            user_id=session['user_id']
        )
        
        db.session.add(new_ad)
        db.session.flush()  # Get the ID
        
        # Add category-specific data
        if category == 'үл хөдлөх':
            real_estate = RealEstate(
                advertisement_id=new_ad.id,
                area=request.form.get('area'),
                location=request.form.get('location'),
                rooms=request.form.get('rooms'),
                floor=request.form.get('floor'),
                garage='garage' in request.form,
                condition=request.form.get('condition'),
                year_built=request.form.get('year_built')
            )
            db.session.add(real_estate)
            
        elif category == 'автомашин':
            automobile = Automobile(
                advertisement_id=new_ad.id,
                manufacturer=request.form.get('manufacturer'),
                model=request.form.get('model'),
                year=request.form.get('year'),
                type=request.form.get('type'),
                engine_capacity=request.form.get('engine_capacity'),
                drive_type=request.form.get('drive_type'),
                transmission=request.form.get('transmission'),
                fuel_type=request.form.get('fuel_type'),
                doors=request.form.get('doors'),
                mileage=request.form.get('mileage'),
                has_plate='has_plate' in request.form
            )
            db.session.add(automobile)
            
        elif category == 'ажил':
            job = Job(
                advertisement_id=new_ad.id,
                sector=request.form.get('sector'),
                sub_sector=request.form.get('sub_sector'),
                position=request.form.get('position'),
                salary=request.form.get('salary'),
                requirements=request.form.get('requirements'),
                degree=request.form.get('degree'),
                experience=request.form.get('experience'),
                location=request.form.get('location')
            )
            db.session.add(job)
        
        # Handle image uploads
        if 'images' in request.files:
            files = request.files.getlist('images')
            for i, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{new_ad.id}_{i}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    image = AdvertisementImage(
                        advertisement_id=new_ad.id,
                        image_path=unique_filename,
                        is_main=(i == 0)  # First image is main
                    )
                    db.session.add(image)
        
        db.session.commit()
        flash('Зар амжилттай нэмэгдлээ!', 'success')
        return redirect(url_for('ad_detail', ad_id=new_ad.id))
    
    return render_template('post_ad.html')

@app.route('/my_ads')
@login_required
def my_ads():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    ads = Advertisement.query.filter_by(user_id=session['user_id'])\
                           .order_by(Advertisement.created_at.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('my_ads.html', ads=ads)

@app.route('/api/latest-ads')
def api_latest_ads():
    ads = Advertisement.query.filter_by(is_active=True)\
                           .order_by(Advertisement.created_at.desc())\
                           .limit(12)\
                           .all()
    
    result = []
    for ad in ads:
        main_image = AdvertisementImage.query.filter_by(advertisement_id=ad.id, is_main=True).first()
        result.append({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'price': float(ad.price) if ad.price else None,
            'created_at': ad.created_at.isoformat(),
            'main_image': main_image.image_path if main_image else None
        })
    
    return {'ads': result}

@app.route('/ad/<int:ad_id>/delete', methods=['POST'])
@login_required
def delete_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.user_id != session['user_id']:
        return {'success': False, 'message': 'Та зөвхөн өөрийн зарaa устгах боломжтой!'}, 403
    
    # Delete images from filesystem
    for image in ad.images:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(ad)
    db.session.commit()
    
    return {'success': True, 'message': 'Зар амжилттай устгагдлаа!'}

@app.route('/ad/<int:ad_id>/activate', methods=['POST'])
@login_required
def activate_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.user_id != session['user_id']:
        return {'success': False, 'message': 'Та зөвхөн өөрийн зарaa идэвхжүүлэх боломжтой!'}, 403
    
    ad.is_active = True
    db.session.commit()
    
    return {'success': True, 'message': 'Зар идэвхжлээ!'}

@app.route('/ad/<int:ad_id>/deactivate', methods=['POST'])
@login_required
def deactivate_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.user_id != session['user_id']:
        return {'success': False, 'message': 'Та зөвхөн өөрийн зарaa идэвхгүй болгох боломжтой!'}, 403
    
    ad.is_active = False
    db.session.commit()
    
    return {'success': True, 'message': 'Зар идэвхгүй боллоо!'}

@app.route('/ad/<int:ad_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ad(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    
    if ad.user_id != session['user_id']:
        flash('Та зөвхөн өөрийн зарaa засах боломжтой!', 'error')
        return redirect(url_for('my_ads'))
    
    if request.method == 'POST':
        ad.title = request.form.get('title')
        ad.description = request.form.get('description')
        ad.price = float(request.form.get('price')) if request.form.get('price') else None
        ad.phone = request.form.get('phone')
        
        # Update category-specific data
        if ad.category == 'үл хөдлөх' and ad.real_estate:
            ad.real_estate.area = request.form.get('area')
            ad.real_estate.location = request.form.get('location')
            ad.real_estate.rooms = request.form.get('rooms')
            ad.real_estate.floor = request.form.get('floor')
            ad.real_estate.garage = 'garage' in request.form
            ad.real_estate.condition = request.form.get('condition')
            ad.real_estate.year_built = request.form.get('year_built')
            
        elif ad.category == 'автомашин' and ad.automobile:
            ad.automobile.manufacturer = request.form.get('manufacturer')
            ad.automobile.model = request.form.get('model')
            ad.automobile.year = request.form.get('year')
            ad.automobile.type = request.form.get('type')
            ad.automobile.engine_capacity = request.form.get('engine_capacity')
            ad.automobile.drive_type = request.form.get('drive_type')
            ad.automobile.transmission = request.form.get('transmission')
            ad.automobile.fuel_type = request.form.get('fuel_type')
            ad.automobile.doors = request.form.get('doors')
            ad.automobile.mileage = request.form.get('mileage')
            ad.automobile.has_plate = 'has_plate' in request.form
            
        elif ad.category == 'ажил' and ad.job:
            ad.job.sector = request.form.get('sector')
            ad.job.sub_sector = request.form.get('sub_sector')
            ad.job.position = request.form.get('position')
            ad.job.salary = request.form.get('salary')
            ad.job.requirements = request.form.get('requirements')
            ad.job.degree = request.form.get('degree')
            ad.job.experience = request.form.get('experience')
            ad.job.location = request.form.get('location')
        
        # Handle new image uploads
        if 'images' in request.files:
            files = request.files.getlist('images')
            for i, file in enumerate(files):
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    unique_filename = f"{ad.id}_{len(ad.images)+i}_{filename}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(file_path)
                    
                    image = AdvertisementImage(
                        advertisement_id=ad.id,
                        image_path=unique_filename,
                        is_main=False
                    )
                    db.session.add(image)
        
        db.session.commit()
        flash('Зар амжилттай шинэчлэгдлээ!', 'success')
        return redirect(url_for('ad_detail', ad_id=ad.id))
    
    return render_template('edit_ad.html', ad=ad)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(session['user_id'])
    
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.phone = request.form.get('phone')
    
    # Handle password change
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if current_password or new_password or confirm_password:
        if not current_password:
            flash('Одоогийн нууц үгээ оруулна уу!', 'error')
            return redirect(url_for('profile'))
        
        if not check_password_hash(user.password_hash, current_password):
            flash('Одоогийн нууц үг буруу байна!', 'error')
            return redirect(url_for('profile'))
        
        if new_password != confirm_password:
            flash('Шинэ нууц үгүүд таарахгүй байна!', 'error')
            return redirect(url_for('profile'))
        
        if len(new_password) < 6:
            flash('Шинэ нууц үг доод тал нь 6 тэмдэгт байх ёстой!', 'error')
            return redirect(url_for('profile'))
        
        user.password_hash = generate_password_hash(new_password)
    
    db.session.commit()
    flash('Профиль амжилттай шинэчлэгдлээ!', 'success')
    return redirect(url_for('profile'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Here you would typically send an email with password reset link
            flash('Нууц үг сэргээх холбоос таны и-мэйл илгээгдлээ!', 'success')
        else:
            flash('Энэ и-мэйл хаягаар бүртгэл олдсонгүй!', 'error')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    ads_query = Advertisement.query.filter_by(is_active=True)
    
    if query:
        ads_query = ads_query.filter(Advertisement.title.contains(query))
    
    if category:
        ads_query = ads_query.filter_by(category=category)
    
    ads = ads_query.order_by(Advertisement.created_at.desc()).limit(20).all()
    
    result = []
    for ad in ads:
        result.append({
            'id': ad.id,
            'title': ad.title,
            'category': ad.category,
            'price': float(ad.price) if ad.price else None,
            'created_at': ad.created_at.isoformat()
        })
    
    return {'results': result}

@app.route('/api/save-ad/<int:ad_id>', methods=['POST'])
@login_required
def api_save_ad(ad_id):
    # This would typically save the ad to user's favorites
    return {'success': True, 'message': 'Зар хадгалагдлаа!'}

@app.route('/api/report-ad/<int:ad_id>', methods=['POST'])
def api_report_ad(ad_id):
    data = request.get_json()
    reason = data.get('reason', '')
    
    # Here you would typically save the report to database
    return {'success': True, 'message': 'Репорт илгээгдлээ!'}

if __name__ == '__main__':
    app.run(debug=True)
