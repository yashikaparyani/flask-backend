from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash , check_password_hash
import psycopg2
from psycopg2 import IntegrityError
import os
from flask_socketio import SocketIO, emit, join_room
import eventlet

eventlet.monkey_patch()

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["https://qconnecttt.netlify.app"])

socketio = SocketIO(app, cors_allowed_origins=["https://qconnecttt.netlify.app"])

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data.get('room', 'quiz_room')
    join_room(room)
    emit('message', {'msg': f'{username} joined the room'}, room=room)

@socketio.on('start_quiz')
def on_start_quiz(data):
    # Admin emits this to start quiz
    emit('quiz_started', data, room='quiz_room')

@socketio.on('next_question')
def on_next_question(data):
    # Admin emits this to move to next question
    emit('question_update', data, room='quiz_room')

def get_db_connection():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise Exception("DATABASE_URL ENVIRONMENT VARIABLE NOT SET")
    conn =psycopg2.connect(DATABASE_URL)
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id SERIAL PRIMARY KEY ,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY ,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            phone TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_stats (
            question_id INTEGER,
            option_index INTEGER,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (question_id, option_index)
        )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

init_db()

@app.route('/', methods=['GET','HEAD'])
def home():
    return "FLASK APP CONNECTED "

@app.route('/leaderboard', methods=['POST'])
def submit_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score')

    if name is None or score is None:
        return jsonify({"error": "Missing name or score"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leaderboard WHERE name = %s", (name,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute("UPDATE leaderboard SET score = %s WHERE username = %s", (score, name))
    else:
        cursor.execute("INSERT INTO leaderboard (username, score) VALUES (%s, %s)", (name, score))
    conn.commit()
    conn.close()


    return jsonify({"message": "Score saved successfully"}), 200

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10")
    results = cursor.fetchall()
    conn.close()

    leaderboard = [{"name": name, "score": score} for name, score in results]
    return jsonify(leaderboard)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not  email  or not password:
        return jsonify({"error": "Missing fields"}), 400
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email =%s",(email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[3], password):
            return jsonify({'success': True,
                            "email": user[2],
                            "role": "admin" if user[2] == "yashikaparyani29@gmail.com" else "user",
                            "username" : user[1]
                            }), 200
        else:
            return jsonify({'success': False,"message": "Invalid email or password"}), 400
    except Exception as e:
        return jsonify({'success': False,"message": str(e)}), 500


@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    if not name or not email or not phone or not password:
        return jsonify({"error": "Missing fields"}), 400
    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        role = data.get('role','user')
        cursor.execute("INSERT INTO users (name, email, password,phone,role) VALUES (%s, %s, %s, %s,%s)", (name, email, hashed_password, phone, role))
        print(f"saved user: {name},{email},{phone}")
        conn.commit()
        conn.close()

        return jsonify({'success':True,"message": "signup successful"}), 200
    except IntegrityError as e:
        return jsonify({'success': False,'message': 'Email already registered'}),400
    except Exception as e:
        return jsonify({'success': False,'message': str(e)}),500


@app.route('/get-users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id": row[0],"name":row[1],"email":row[2],"phone":row[4]}
        for row in users
    ])
@app.route('/all-leaderboard', methods=['GET'])
def all_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leaderboard")
    results = cursor.fetchall()
    conn.close()

    full_data = [{"id": row[0], "name": row[1], "score": row[2]} for row in results]
    return jsonify(full_data), 200

@app.route('/submit-option', methods=['POST'])
def submit_option():
    data = request.get_json()
    question_id = data.get('question_id')
    option_index = data.get('option_index')


    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if entry already exists
    cursor.execute('''
        SELECT count FROM question_stats
        WHERE question_id = %s AND option_index = %s
    ''', (question_id, option_index))
    row = cursor.fetchone()

    if row:
        cursor.execute('''
            UPDATE question_stats
            SET count = count + 1
            WHERE question_id = %s AND option_index = %s
        ''', (question_id, option_index))
    else:
        cursor.execute('''
            INSERT INTO question_stats (question_id, option_index, count)
            VALUES (%s, %s, %s)
        ''', (question_id, option_index, 1))

    conn.commit()
    conn.close()

    return jsonify({
    'status': 'success',
    'step': 'submitted',
    'question_id': question_id,
    'option_index': option_index,
    'existing_row': bool(row)
    })

@app.route('/get-percentages/<int:question_id>', methods=['GET'])
def get_percentages(question_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT option_index, count FROM question_stats WHERE question_id = %s
    ''', (question_id,))
    rows = cursor.fetchall()

    total = sum(count for _, count in rows)
    if total == 0:
        return jsonify({})  # No data yet

    percentages = {
        str(option_index): round((count / total) * 100, 2)
        for option_index, count in rows
    }

    return jsonify([percentages.get("0", 0),
    percentages.get("1", 0),
    percentages.get("2", 0),
    percentages.get("3", 0)])


@app.route('/view-stats')
def view_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM question_stats')
    data = cursor.fetchall()
    conn.close()
    return jsonify(data)

@app.route('/live-scores', methods=['GET'])
def live_scores():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10")
    data = cursor.fetchall()
    conn.close()

    scores = [{'name': row[0], 'score': row[1]} for row in data]
    return jsonify(scores)

@app.route('/update-live-score', methods=['POST'])
def update_live_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Agar naam already leaderboard mein hai, toh update karo
    cursor.execute('SELECT * FROM leaderboard WHERE name = %s', (name,))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('UPDATE leaderboard SET score = %s WHERE name = %s', (score, name))
    else:
        cursor.execute('INSERT INTO leaderboard (name, score) VALUES (%s, %s)', (name, score))

    conn.commit()
    conn.close()
    return jsonify({'message': 'Live score updated'})

if __name__== '__main__':
    init_db()
    from os import environ
    port = int(environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)