import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
from database import get_db_connection, init_db

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_key_change_in_production'

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Initialize database
init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/listings')
def api_listings():
    conn = get_db_connection()
    query = "SELECT * FROM books WHERE status = 'available'"
    params = []
    
    search = request.args.get('search', '')
    subject = request.args.get('subject', '')
    condition = request.args.get('condition', '')
    
    if search:
        query += " AND (title LIKE ? OR author LIKE ?)"
        params.extend([f'%{search}%', f'%{search}%'])
    if subject:
        query += " AND subject = ?"
        params.append(subject)
    if condition:
        query += " AND condition = ?"
        params.append(condition)
        
    query += " ORDER BY created_at DESC"
    
    books = conn.execute(query, params).fetchall()
    conn.close()
    
    book_list = [dict(book) for book in books]
    return jsonify(book_list)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        password = request.form['password']
        
        if not name or not email or not password:
            flash('Please fill out all required fields.', 'danger')
            return redirect(url_for('register'))
            
        password_hash = generate_password_hash(password)
        
        # Check if email already exists
        conn = get_db_connection()
        existing_user = conn.execute('SELECT id FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if existing_user:
            flash('Email address already exists.', 'danger')
            return redirect(url_for('register'))
            
        # Generate OTP (6 digits)
        otp = str(random.randint(100000, 999999))
        
        # Save temp registration data in session
        session['reg_name'] = name
        session['reg_email'] = email
        session['reg_phone'] = phone
        session['reg_password_hash'] = password_hash
        session['reg_otp'] = otp
        session['reg_otp_time'] = time.time()
        
        # Send OTP email
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT', 587))
        smtp_username = os.environ.get('SMTP_USERNAME')
        smtp_password = os.environ.get('SMTP_PASSWORD')
        
        if not all([smtp_server, smtp_username, smtp_password]):
            print(f"[DEVELOPMENT MODE] OTP for {email} is: {otp}")
            # flash('OTP generated. Check console for development.', 'info')
        else:
            try:
                msg = MIMEMultipart()
                msg['From'] = smtp_username
                msg['To'] = email
                msg['Subject'] = "Your Student Book Exchange Verification Code"
                
                body = f"Hello {name},\n\nYour verification code is: {otp}\n\nThis code will expire in 5 minutes.\n\nThank you!"
                msg.attach(MIMEText(body, 'plain'))
                
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
                server.quit()
            except Exception as e:
                print(f"Failed to send email: {e}")
                flash('Failed to send verification email. Please try again.', 'danger')
                return redirect(url_for('register'))
                
        return redirect(url_for('verify_otp'))
            
    return render_template('register.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reg_email' not in session:
        flash('Registration session expired. Please register again.', 'warning')
        return redirect(url_for('register'))
        
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        stored_otp = session.get('reg_otp')
        otp_time = session.get('reg_otp_time', 0)
        
        # Check if 5 minutes have passed
        if time.time() - otp_time > 300:
            session.pop('reg_otp', None) # Clear expired OTP
            flash('OTP has expired. Please register again.', 'danger')
            return redirect(url_for('register'))
            
        if user_otp == stored_otp:
            # OTP is correct, insert user into DB
            conn = get_db_connection()
            try:
                conn.execute('INSERT INTO users (name, email, phone, password_hash) VALUES (?, ?, ?, ?)',
                             (session['reg_name'], session['reg_email'], session['reg_phone'], session['reg_password_hash']))
                conn.commit()
                flash('Registration successful! Please log in.', 'success')
                
                # Clear registration session data
                for key in ['reg_name', 'reg_email', 'reg_phone', 'reg_password_hash', 'reg_otp', 'reg_otp_time']:
                    session.pop(key, None)
                    
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Email address already exists.', 'danger')
                return redirect(url_for('register'))
            finally:
                conn.close()
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            
    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_ad():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        subject = request.form.get('subject', '')
        condition = request.form['condition']
        price = request.form['price']
        description = request.form.get('description', '')
        
        if not title or not author or not condition or not price:
            flash('Title, author, condition, and price are required.', 'danger')
            return redirect(url_for('post_ad'))
            
        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except ValueError:
            flash('Price must be a valid positive number.', 'danger')
            return redirect(url_for('post_ad'))
            
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # To prevent naming collisions, prepend a timestamp
                import time
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO books (user_id, title, author, subject, condition, price, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session['user_id'], title, author, subject, condition, price, description, image_path))
        conn.commit()
        conn.close()
        
        flash('Ad posted successfully!', 'success')
        return redirect(url_for('index'))
        
    return render_template('post_ad.html')

@app.route('/listing/<int:id>')
def listing_detail(id):
    conn = get_db_connection()
    book = conn.execute('SELECT b.*, u.name, u.email, u.phone FROM books b JOIN users u ON b.user_id = u.id WHERE b.id = ?', (id,)).fetchone()
    conn.close()
    
    if not book:
        flash('Listing not found.', 'danger')
        return redirect(url_for('index'))
        
    return render_template('listing_detail.html', book=book)

@app.route('/my-listings')
@login_required
def my_listings():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM books WHERE user_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('my_listings.html', books=books)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ad(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    
    if not book:
        conn.close()
        flash('Listing not found.', 'danger')
        return redirect(url_for('my_listings'))
        
    if book['user_id'] != session['user_id']:
        conn.close()
        flash('You do not have permission to edit this ad.', 'danger')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        subject = request.form.get('subject', '')
        condition = request.form['condition']
        price = request.form['price']
        description = request.form.get('description', '')
        
        if not title or not author or not condition or not price:
            flash('Title, author, condition, and price are required.', 'danger')
            return redirect(url_for('edit_ad', id=id))
            
        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except ValueError:
            flash('Price must be a valid positive number.', 'danger')
            return redirect(url_for('edit_ad', id=id))
            
        image_path = book['image_path']
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                import time
                filename = f"{int(time.time())}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"

        conn.execute('''
            UPDATE books SET title = ?, author = ?, subject = ?, condition = ?, price = ?, description = ?, image_path = ?
            WHERE id = ?
        ''', (title, author, subject, condition, price, description, image_path, id))
        conn.commit()
        conn.close()
        
        flash('Ad updated successfully!', 'success')
        return redirect(url_for('my_listings'))
        
    conn.close()
    return render_template('edit_ad.html', book=book)

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_ad(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    
    if book and book['user_id'] == session['user_id']:
        conn.execute('DELETE FROM books WHERE id = ?', (id,))
        conn.commit()
        flash('Ad deleted successfully.', 'success')
    else:
        flash('Unauthorized action.', 'danger')
        
    conn.close()
    return redirect(url_for('my_listings'))

@app.route('/mark-sold/<int:id>', methods=['POST'])
@login_required
def mark_sold(id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM books WHERE id = ?', (id,)).fetchone()
    
    if book and book['user_id'] == session['user_id']:
        conn.execute('UPDATE books SET status = ? WHERE id = ?', ('sold', id))
        conn.commit()
        flash('Ad marked as sold.', 'success')
    else:
        flash('Unauthorized action.', 'danger')
        
    conn.close()
    return redirect(url_for('my_listings'))

@app.route('/inbox')
@login_required
def inbox():
    conn = get_db_connection()
    user_id = session['user_id']
    
    # Get the latest message for each conversation the user is part of
    # This query uses group by to get the most recent message per conversation partner
    query = '''
        SELECT m.*, 
               u.name as other_user_name,
               u.id as other_user_id
        FROM messages m
        JOIN users u ON u.id = CASE 
                                WHEN m.sender_id = ? THEN m.receiver_id 
                                ELSE m.sender_id 
                              END
        WHERE m.id IN (
            SELECT MAX(id)
            FROM messages
            WHERE sender_id = ? OR receiver_id = ?
            GROUP BY CASE 
                        WHEN sender_id = ? THEN receiver_id 
                        ELSE sender_id 
                     END
        )
        ORDER BY m.created_at DESC
    '''
    conversations = conn.execute(query, (user_id, user_id, user_id, user_id)).fetchall()
    conn.close()
    
    return render_template('inbox.html', conversations=conversations)

@app.route('/chat/<int:other_user_id>', methods=['GET', 'POST'])
@login_required
def chat(other_user_id):
    if other_user_id == session['user_id']:
        flash('You cannot message yourself.', 'warning')
        return redirect(url_for('inbox'))
        
    conn = get_db_connection()
    other_user = conn.execute('SELECT id, name FROM users WHERE id = ?', (other_user_id,)).fetchone()
    
    if not other_user:
        conn.close()
        flash('User not found.', 'danger')
        return redirect(url_for('inbox'))
        
    if request.method == 'POST':
        content = request.form.get('content')
        book_id = request.form.get('book_id') or None
        
        if content:
            conn.execute('''
                INSERT INTO messages (sender_id, receiver_id, book_id, content) 
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], other_user_id, book_id, content))
            conn.commit()
            
    # Mark messages as read
    conn.execute('''
        UPDATE messages SET is_read = 1 
        WHERE sender_id = ? AND receiver_id = ? AND is_read = 0
    ''', (other_user_id, session['user_id']))
    conn.commit()
    
    # Get chat history
    messages = conn.execute('''
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY created_at ASC
    ''', (session['user_id'], other_user_id, other_user_id, session['user_id'])).fetchall()
    
    # Check if there's a specific book context passed in the URL (for initial message context)
    book_context = None
    book_id_param = request.args.get('book_id')
    if book_id_param:
        book_context = conn.execute('SELECT id, title FROM books WHERE id = ?', (book_id_param,)).fetchone()
        
    conn.close()
    
    return render_template('chat.html', 
                           other_user=other_user, 
                           messages=messages, 
                           book_context=book_context)

if __name__ == '__main__':
    app.run(debug=True)
