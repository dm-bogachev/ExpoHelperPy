import os
from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app) 

@app.route('/')
def serve_main_html():
    return send_from_directory('./src/main', 'main.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('./src', path)

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')