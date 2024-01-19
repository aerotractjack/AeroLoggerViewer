from flask import Flask, jsonify, request
from filelock import FileLock

from aerologger import AeroLogger

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

@app.route("/read_log", methods=['GET', 'POST'])
def read_log(data=None):
    if data is None:
        data = request.get_json()
    lock_path = data.get('lock_path')
    log_path = data.get('log_path')
    n_lines = data.get('n_lines')

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
        "lock_path": "/home/aerotract/microservice_logs/UPQ/UPQ.log.lock",
        "log_path": "/home/aerotract/microservice_logs/UPQ/UPQ.log",
        "n_lines": 20
    }
    return read_log(preset_data)

if __name__ == "__main__":
    from waitress import serve
    serve(app, port=27895, host="127.0.0.1")