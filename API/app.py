from flask import Flask, jsonify, request
import os
from pathlib import Path
from filelock import FileLock

from aerologger import AeroLoggerBase

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

def read(filename):
    with open(filename, "r") as fp:
        return fp.read()

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
def read_log():
    data = request.get_json()
    lock_path = data.get('lock_path')
    log_path = data.get('log_path')

    if not all([lock_path, log_path]):
        return "Missing data", 400
    with FileLock(lock_path):
        contents = read(log_path)
    return jsonify(contents)


if __name__ == "__main__":
    from waitress import serve
    serve(app, port=27895, host="0.0.0.0")