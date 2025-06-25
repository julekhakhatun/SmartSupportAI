from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)


@app.route('/api/ask', methods=['POST'])
def ask():
    print("=== Incoming Request ===")
    print("Content-Type:", request.headers.get('Content-Type'))
    print("Raw Data:", request.data.decode())

    if request.is_json:
        data = request.get_json()
        print("Parsed JSON:", data)
        return jsonify({'response': f"You said: {data.get('prompt', 'nothing')}"})
    else:
        print("Not JSON")
        return jsonify({'error': 'Request must be JSON'}), 415

if __name__ == '__main__':
    app.run(debug=True)
