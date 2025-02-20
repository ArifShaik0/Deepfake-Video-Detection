from flask import Flask, render_template, request, redirect, url_for, flash
import os
import sqlite3
from werkzeug.utils import secure_filename
import tensorflow as tf
from model_script import classify_video


app = Flask(__name__)

app.secret_key = 'your_secret_key'

# Configure the upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the model once when the app starts
model = tf.keras.models.load_model('used_model.keras')  # Adjust path as necessary

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signup', methods=['POST'])
def handle_signup():
    # Get the form data
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Save the user credentials in the database
    conn = sqlite3.connect('user_data.db')  # Connect to the database
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Insert the user's data
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                       (username, email, password))
        conn.commit()
    except sqlite3.IntegrityError:
        # Handle duplicate email error
        conn.close()
        return "Email already exists. Please try a different one."

    conn.close()

    # Redirect to the login page after successful signup
    return redirect(url_for('login'))  # Assuming 'index' is the login page

@app.route('/login', methods=['POST'])
def handle_login():
    # Get the form data
    email = request.form['email']
    password = request.form['password']

    # Validate credentials
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Login successful, redirect to the home page
        return redirect(url_for('home'))
    else:
        # Flash an error message and reload the login page
        flash('Invalid email or password. Please try again.')
        return redirect(url_for('login'))


@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Classify the video using the custom CNN model
        result = classify_video(filepath, model=model)

        # Remove the uploaded file after processing
        os.remove(filepath)

        return render_template('result.html', result=result)

    return redirect(request.url)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
