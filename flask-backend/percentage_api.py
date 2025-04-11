from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'leaderboard.db'

@app.route('/submit-option', methods=['POST'])
def submit_option():
    data = request.get_json()
    question_id = data.get('question_id')
    option_index = data.get('option_index')

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS question_stats (question_id INTEGER, option_index INTEGER, count INTEGER, PRIMARY KEY (question_id, option_index))')

    c.execute('SELECT count FROM question_stats WHERE question_id = ? AND option_index = ?', (question_id, option_index))
    result = c.fetchone()

    if result:
        c.execute('UPDATE question_stats SET count = count + 1 WHERE question_id = ? AND option_index = ?', (question_id, option_index))
    else:
        c.execute('INSERT INTO question_stats (question_id, option_index, count) VALUES (?, ?, ?)', (question_id, option_index, 1))

    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/get-percentages/<int:question_id>', methods=['GET'])
def get_percentages(question_id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT option_index, count FROM question_stats WHERE question_id = ?', (question_id,))
    rows = c.fetchall()
    conn.close()

    total = sum([row[1] for row in rows])
    result = {}

    for option_index, count in rows:
        result[option_index] = round((count / total) * 100, 2) if total > 0 else 0

    return jsonify(result)

# For Render deployment
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5501))
    app.run(host="0.0.0.0", port=port)