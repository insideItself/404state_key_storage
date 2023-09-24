from flask import Flask, jsonify
from flask_cors import CORS
from config import FLASK_APP_PORT
import socket
from database.database_manager import DatabaseManager


app = Flask(__name__)
CORS(app)


@app.route("/")
def return_key():

    return f"Container ID: {socket.gethostname()}"


@app.route("/key/<name>/<uuid>")
def get_key_by_name_and_uuid(name: str, uuid: str):

    try:
        # Validate parameters
        if not name or not uuid:
            return jsonify({"error": "Both name and uuid are required"}), 400

        # Fetch data from the database
        db_manager: DatabaseManager = DatabaseManager()
        key_data: dict[str, any] = db_manager.get_key_by_uuid(name=name, uuid=uuid)
        db_manager.close()

        # Check if data exists
        if key_data:
            return jsonify(key_data)
        else:
            return jsonify({"error": "Data not found"}), 404

    except Exception as e:
        # Handle other unforeseen errors
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(port=FLASK_APP_PORT)
