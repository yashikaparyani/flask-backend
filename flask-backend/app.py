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

@app.route('/login', methods=['GET','POST']) 
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

@app.route('/submit_score', methods=['GET','POST']) 
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

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    if request.method == 'GET':
        data = db.all()
        sorted_data = sorted(data, key=lambda x: x['score'], reverse=True)
        return jsonify(sorted_data)
    
    if request.method == 'POST':
        data = request.get_json()
        if not data or 'name' not in data or 'score' not in data:
            return jsonify({'error': 'Invalid data'}), 400
        db.insert({'name': data['name'], 'score': data['score']})
        return jsonify({'message': 'Score saved successfully'})

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