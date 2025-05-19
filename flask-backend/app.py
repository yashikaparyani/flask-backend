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
def on_start_quiz(data=None):
    # Admin emits this to start quiz
    emit('quiz_started', data or {} ,room='quiz_room')

@socketio.on('next_question')
def on_next_question(data):
    # Admin emits this to move to next question
    try:
        if not data or 'questionData' not in data:
            return {'success': False, 'message': 'Invalid question data format'}
            
        # Validate question data structure
        question_data = data['questionData']
        required_fields = ['question', 'options', 'answer']
        if not all(field in question_data for field in required_fields):
            return {'success': False, 'message': 'Missing required fields in question data'}
            
        # Emit the question update to all clients in the quiz room
        emit('question_update', data, room='quiz_room')
        return {'success': True, 'message': 'Question updated successfully'}
    except Exception as e:
        print(f"Error in next_question: {str(e)}")
        return {'success': False, 'message': str(e)}

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
    total_questions = data.get('total_questions', 10)  # Default to 10 if not provided

    if name is None or score is None:
        return jsonify({"error": "Missing name or score"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if user exists
        cursor.execute("SELECT * FROM leaderboard WHERE name = %s", (name,))
        existing = cursor.fetchone()

        if existing:
            # Update score if new score is higher
            if score > existing[2]:  # existing[2] is the current score
                cursor.execute("UPDATE leaderboard SET score = %s WHERE name = %s", (score, name))
        else:
            # Insert new score
            cursor.execute("INSERT INTO leaderboard (name, score) VALUES (%s, %s)", (name, score))

        conn.commit()
        return jsonify({
            "message": "Score saved successfully",
            "name": name,
            "score": score,
            "total_questions": total_questions
        }), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Get all scores ordered by score descending
        cursor.execute("""
            SELECT name, score 
            FROM leaderboard 
            ORDER BY score DESC
        """)
        results = cursor.fetchall()
        
        # Format the response with rankings
        leaderboard = []
        for rank, (name, score) in enumerate(results, 1):
            leaderboard.append({
                "rank": rank,
                "name": name,
                "score": score
            })
            
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

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
        # Return array of zeros if no data
        return jsonify([0, 0, 0, 0])

    # Initialize percentages array with zeros
    percentages = [0, 0, 0, 0]
    
    # Calculate percentages for each option
    for option_index, count in rows:
        if option_index < 4:  # Ensure we only process valid option indices
            percentages[option_index] = round((count / total) * 100, 2)

    conn.close()
    return jsonify(percentages)


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
    try:
        # Get top 10 scores, ordered by score descending
        cursor.execute("""
            SELECT name, score 
            FROM leaderboard 
            ORDER BY score DESC 
            LIMIT 10
        """)
        data = cursor.fetchall()
        
        # Format the response
        scores = [{'name': row[0], 'score': row[1]} for row in data]
        return jsonify(scores)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/update-live-score', methods=['POST'])
def update_live_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score')

    if not name or score is None:
        return jsonify({'error': 'Missing name or score'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Check if user exists in leaderboard
        cursor.execute('SELECT * FROM leaderboard WHERE name = %s', (name,))
        existing = cursor.fetchone()

        if existing:
            # Update score if it's higher than existing score
            if score > existing[2]:  # existing[2] is the current score
                cursor.execute('UPDATE leaderboard SET score = %s WHERE name = %s', (score, name))
        else:
            # Insert new score
            cursor.execute('INSERT INTO leaderboard (name, score) VALUES (%s, %s)', (name, score))

        conn.commit()
        return jsonify({'message': 'Live score updated successfully'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

if __name__== '__main__':
    init_db()
    from os import environ
    port = int(environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)