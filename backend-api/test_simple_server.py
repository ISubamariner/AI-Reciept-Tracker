"""Simple test server to verify Flask basics work."""
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/test', methods=['GET', 'POST'])
def test():
    return jsonify({'message': 'Test endpoint works!', 'method': 'GET or POST'})

@app.route('/api/auth/login', methods=['POST'])
def test_login():
    return jsonify({'message': 'Simple login test', 'status': 'ok'})

if __name__ == '__main__':
    print("Starting simple test server...")
    app.run(host='127.0.0.1', port=5000, debug=False)
