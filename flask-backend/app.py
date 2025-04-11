from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://qconnecttt.netlify.app"}}, supports_credentials=True)

DB_PATH = os.path.join(os.path.dirname(__file__), "leaderboard.db")

@app.route("/")
def home():
    return "Flask backend for Qnect is running."

@app.route("/submit-score", methods=["POST"])
def submit_score():
    data = request.get_json()
    name = data.get("name")
    score = data.get("score")

    if not name or score is None:
        return jsonify({"error": "Missing name or score"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO leaderboard (name, score) VALUES (?, ?)", (name, score))
        conn.commit()
        conn.close()
        return jsonify({"message": "Score submitted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10")
        rows = cursor.fetchall()
        conn.close()

        leaderboard = [{"name": row[0], "score": row[1]} for row in rows]
        return jsonify(leaderboard)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/submit-user", methods=["POST"])
def submit_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")

    if not name or not email or not phone:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        conn.close()
        return jsonify({"message": "User data submitted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
            selected_option = str(answer.get("selected_option"))

            if question_id is not None and selected_option:
                cursor.execute("""
                    INSERT INTO question_stats (question_id, option_selected, count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(question_id, option_selected)
                    DO UPDATE SET count = count + 1
                """, (question_id, selected_option))

        conn.commit()
        conn.close()
        return jsonify({"message": "Answers saved successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/question-stats", methods=["GET"])
def get_question_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT question_id, option_selected, count FROM question_stats")
        rows = cursor.fetchall()
        conn.close()

        stats = {}
        for row in rows:
            q_index = row[0]
            o_index = int(row[1])
            count = row[2]
            if q_index not in stats:
                stats[q_index] = {}
            stats[q_index][o_index] = count

        return jsonify(stats)

    except Exception as e:
        print("ERROR in /question-stats:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)