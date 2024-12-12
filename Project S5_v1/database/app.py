from flask import Flask, request, jsonify, session, redirect, url_for
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management
socketio = SocketIO(app)

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('healmount.db')  # SQLite database file
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

# Create the database schema (run once)
def create_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        name TEXT,
        surname TEXT,
        birthdate TEXT,
        education TEXT,
        experience TEXT
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        specialization TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        date_of_birth DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        patient_id INTEGER,
        appointment_date TIMESTAMP,
        status TEXT DEFAULT 'scheduled',
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS blocked_time_slots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        start_datetime TIMESTAMP,
        end_datetime TIMESTAMP,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        doctor_id INTEGER,
        patient_id INTEGER,
        message TEXT NOT NULL,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_at TIMESTAMP,
        FOREIGN KEY (doctor_id) REFERENCES doctors(id),
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )''')
    
    conn.commit()
    conn.close()

# Register User (save info into the database)
@app.route('/api/register/user', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data['name']
    surname = data['surname']
    email = data['email']
    password = data['password']
    birthdate = data['birthdate']
    education = data['education']
    experience = data['experience']

    # Hash the password
    hashed_password = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO users (name, surname, email, password, birthdate, education, experience)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''',
                   (name, surname, email, hashed_password, birthdate, education, experience))
    conn.commit()
    conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

# User Login (check credentials)
@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user['password'], password):
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

# Register Doctor
@app.route('/api/register/doctor', methods=['POST'])
def register_doctor():
    data = request.get_json()
    name = data['name']
    email = data['email']
    phone = data.get('phone', '')
    specialization = data['specialization']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO doctors (name, email, phone, specialization)
                      VALUES (?, ?, ?, ?)''', (name, email, phone, specialization))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Doctor registered successfully'}), 201

# Register Patient
@app.route('/api/register/patient', methods=['POST'])
def register_patient():
    data = request.get_json()
    name = data['name']
    email = data['email']
    phone = data.get('phone', '')
    date_of_birth = data['date_of_birth']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO patients (name, email, phone, date_of_birth)
                      VALUES (?, ?, ?, ?)''', (name, email, phone, date_of_birth))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Patient registered successfully'}), 201

# Send Message
@app.route('/api/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    doctor_id = data['doctor_id']
    patient_id = data['patient_id']
    message = data['message']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO messages (doctor_id, patient_id, message)
                      VALUES (?, ?, ?)''', (doctor_id, patient_id, message))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Message sent successfully'}), 201

# Start the app with socketio
@socketio.on('connect')
def handle_connect():
    print("User connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("User disconnected")

# SocketIO events for messages, offers, answers, and candidates
@socketio.on('offer')
def handle_offer(offer_data):
    emit('offer', offer_data, room=offer_data['target_user_id'])

@socketio.on('answer')
def handle_answer(answer_data):
    emit('answer', answer_data, room=answer_data['target_user_id'])

@socketio.on('candidate')
def handle_candidate(candidate_data):
    emit('candidate', candidate_data, room=candidate_data['target_user_id'])

if __name__ == '__main__':
    create_db()  # Create the database and tables if they don't exist
    socketio.run(app, debug=True)
