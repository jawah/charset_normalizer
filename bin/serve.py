from flask import Flask, jsonify, send_from_directory
from glob import glob

app = Flask(__name__)


@app.route('/raw/<path:path>')
def read_file(path):
    return send_from_directory('../char-dataset', path, as_attachment=True), 200, {"Content-Type": "text/plain"}


@app.route("/")
def read_targets():
    return jsonify(
        [
            el.replace("./char-dataset", "/raw").replace("\\", "/") for el in glob("./char-dataset/**/*")
        ]
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080)
