from flask import Flask, request, jsonify 
from flask_cors import CORS 
from tinydb import TinyDB, Query

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

db = TinyDB('leaderboard.json') 
leaderboard_table = db.table('scores')

@app.route('/') 
def home(): 
    return "Qnect Backend Running"

#Login route

@app.route('/login', methods=['POST']) 
def login(): 
    data = request.get_json() 
    name = data.get('name') 
    email = data.get('email') 
    password = data.get('password') 
    phone = data.get('phone')

    if not all([name, email, password, phone]):
        return jsonify({'message': 'Missing fields'}), 400

    print(f"User Logged In: {name}, {email}, {phone}")
    return jsonify({'message': 'Login successful'}), 200

#Submit score to leaderboard

@app.route('/submit_score', methods=['POST']) 
def submit_score(): 
    data = request.get_json() 
    name = data.get('name') 
    score = data.get('score')

    if name is None or score is None:
        return jsonify({'message': 'Missing name or score'}), 400

    leaderboard_table.insert({'name': name, 'score': score})
    print(f"Score submitted: {name} - {score}")
    return jsonify({'message': 'Score submitted successfully'}), 200

#Get leaderboard

@app.route('/leaderboard', methods=['GET']) 
def leaderboard(): 
    scores = leaderboard_table.all() 
    return jsonify(scores), 200

#Reset leaderboard

@app.route('/reset_leaderboard', methods=['DELETE']) 
def reset_leaderboard(): 
    leaderboard_table.truncate() 
    print("Leaderboard reset.") 
    return jsonify({'message': 'Leaderboard reset successfully'}), 200

if __name__ == '__main__': 
    import os
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)