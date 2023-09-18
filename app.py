from flask import Flask, jsonify
from flask_cors import CORS
from config import SERVER, SERVER_PORT, PASSWORD

app = Flask(__name__)
CORS(app)


@app.route("/")
def return_key():
    key_test: dict[str, any] = {
      "server": SERVER,
      "server_port": SERVER_PORT,
      "password": PASSWORD,
      "method": "chacha20-ietf-poly1305"
    }

    return jsonify(key_test)


if __name__ == "__main__":
    app.run(port=8000)