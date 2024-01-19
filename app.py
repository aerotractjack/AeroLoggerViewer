from flask import Flask, jsonify
from pathlib import Path

from aerologger import AeroLogger


app = Flask(__name__)

def read_locked(lock_path, log_path, lines):
    pass

@app.route("/health", methods=['GET', 'POST'])
def health():
    return jsonify("healthy"), 200

if __name__ == "__main__":
    from waitress import serve
    serve(app, port=27895, host="127.0.0.1")