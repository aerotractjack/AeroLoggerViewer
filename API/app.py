from flask import Flask, jsonify, request
import os
from pathlib import Path
from filelock import FileLock

from aerologger import AeroLoggerBase

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def read_last_n_lines(filename, n_lines):
    with open(filename, 'rb') as file:
        file.seek(0, 2)  
        size = file.tell()
        buffer = bytearray()
        lines = 0
        for _ in range(size):
            file.seek(-2, 1)
            char = file.read(1)
            if char == b'\n':
                lines += 1
                if lines >= n_lines:
                    break
            buffer.extend(char)
        return buffer[::-1].decode()

@app.route("/health", methods=['GET', 'POST'])
def health():
    return jsonify("healthy"), 200

@app.route("/describe_logs", methods=['GET'])
def describe_logs():
    logs = {}
    for logd in os.listdir(AeroLoggerBase):
        logs[logd] = {
            "log_path": (Path(AeroLoggerBase)/logd/logd).with_suffix(".log").as_posix(),
            "lock_path": (Path(AeroLoggerBase)/logd/logd).with_suffix(".log.lock").as_posix()
        }
    return jsonify(logs), 200

@app.route("/read_log", methods=['GET', 'POST'])
def read_log(data=None):
    if data is None:
        data = request.get_json()
    lock_path = data.get('lock_path')
    log_path = data.get('log_path')
    n_lines = data.get('n_lines', 100)

    if not all([lock_path, log_path, n_lines]):
        return "Missing data", 400
    try:
        n_lines = int(n_lines)
    except ValueError:
        return "Invalid n_lines", 400
    with FileLock(lock_path):
        contents = read_last_n_lines(log_path, n_lines)
    return jsonify(contents)

@app.route("/read_log_example", methods=['GET', 'POST'])
def read_log_example():
    preset_data = {
        "name": "UPQ",
        "n_lines": 50
    }
    return read_log(preset_data)

@app.route("/describe_logs_example", methods=['GET'])
def describe_logs_example():
    return describe_logs()

if __name__ == "__main__":
    from waitress import serve
    serve(app, port=27895, host="127.0.0.1")