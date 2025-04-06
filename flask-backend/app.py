from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow frontend access
db = TinyDB('leaderboard.json')
User = Query()

@app.route('/submit-score', methods=['POST'])
def submit_score():
    data = request.get_json()
    username = data['username']
    score = data['score']

    existing = db.search(User.username == username)
    if existing:
        if score > existing[0]['score']:
            db.update({'score': score}, User.username == username)
    else:
        db.insert({'username': username, 'score': score})
    return jsonify({"message": "Score saved."})

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    results = db.all()
    sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
    return jsonify(sorted_results[:10])

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)