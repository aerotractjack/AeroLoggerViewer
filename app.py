from flask import Flask, jsonify

from aerologger import AeroLogger

dup_logger = AeroLogger(
    'DUP',
    'DUP/DUP.log'
)

app = Flask(__name__)

@app.route("/health", methods=['GET', 'POST'])
def health():
    return jsonify("healthy"), 200

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=95831)