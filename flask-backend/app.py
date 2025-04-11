from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, origins=["https://qconnecttt.netlify.app"])

DB_PATH = os.path.join(os.path.dirname(__file__), 'leaderboard.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS question_stats (
            question_id INTEGER,
            option_selected TEXT,
            count INTEGER DEFAULT 0,
            PRIMARY KEY (question_id, option_selected)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return "Quiz Leaderboard API is Running!"

@app.route('/leaderboard', methods=['POST'])
def submit_score():
    data = request.get_json()
    name = data.get('name')
    score = data.get('score')

    if name is None or score is None:
        return jsonify({"error": "Missing name or score"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO leaderboard (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()

    return jsonify({"message": "Score saved successfully"}), 200

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10")
    results = cursor.fetchall()
    conn.close()

    leaderboard = [{"name": name, "score": score} for name, score in results]
    return jsonify(leaderboard)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not name or not email or not phone:
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
    print(f"saved user: {name},{email},{phone}")
    conn.commit()
    conn.close()

    return jsonify({"message": "Login successful"}), 200

@app.route('/get-users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify([
        {"id": row[0],"name":row[1],"email":row[2],"phone":row[3]}
        for row in users
    ])
@app.route('/all-leaderboard', methods=['GET'])
def all_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM leaderboard")
    results = cursor.fetchall()
    conn.close()

    full_data = [{"id": row[0], "name": row[1], "score": row[2]} for row in results]
    return jsonify(full_data), 200

@app.route('/submit-answers', methods=['POST'])
def submit_answers():
    data = request.get_json()
    answers = data.get('answers')

    if not answers:
        return jsonify({"error": "Answers data missing"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        for answer in answers:
            question_id = answer.get("question_id")
            selected_option = answer.get("selected_option")

            if question_id is not None and selected_option:
                cursor.execute(
                    "INSERT INTO question_stats (question_id, selected_option) VALUES (?, ?)",
                    (question_id, selected_option)
                )

        conn.commit()
        conn.close()

        return jsonify({"message": "Answers saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/question-stats', methods=['GET'])
def question_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT question_id, selected_option, COUNT(*) FROM answers GROUP BY question_id, selected_option")
        results = cursor.fetchall()
        print("Query Results:", results)

        stats = {}
        for qid, option, count in results:
            if qid not in stats:
                stats[qid] = {}
            stats[qid][option] = count

        percentages = {}
        for qid in stats:
            total = sum(stats[qid].values())
            percentages[qid] = {
                opt: round((count / total) * 100, 2)
                for opt, count in stats[qid].items()
            }

        return jsonify(percentages)
    
    except Exception as e:
        print("Error in /question-stats:", e)
        return jsonify({"error": str(e)}), 500


if __name__== '__main__':
    from os import environ
    port = int(environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)