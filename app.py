from flask import Flask
from flask_cors import CORS
from config import FLASK_APP_PORT
import socket

app = Flask(__name__)
CORS(app)


@app.route("/")
def return_key():

    return f"Container ID: {socket.gethostname()}"


if __name__ == "__main__":
    app.run(port=FLASK_APP_PORT)
