import requests
from flask import Flask, jsonify, request, abort
from flask_cors import cross_origin
from config import FLASK_APP_PORT, check_auth
import socket
from database.database_manager import DatabaseManager


app = Flask(__name__)


@app.before_request
def before_request():
    # Skip authentication for the GET endpoint
    if request.method == 'GET' and request.path.startswith('/key/'):
        return
    auth = request.authorization
    if not check_auth(auth):
        abort(401)


@app.route("/")
def return_key():

    return f"Container ID: {socket.gethostname()}"


@app.route("/key/<name>/<uuid>", methods=['GET'])
@cross_origin()  # turn on CORS to make this endpoint available from Outline Client
def get_key_by_name_and_uuid(name: str, uuid: str):

    try:
        # Validate parameters
        if not name or not uuid:
            return jsonify({"error": "Both name and uuid are required"}), 400

        # Fetch data from the database
        db_manager: DatabaseManager = DatabaseManager()
        key_data: dict[str, any] = db_manager.get_key(name=name, uuid=uuid)
        db_manager.close()

        # Check if data exists
        if key_data:
            return jsonify(key_data)
        else:
            return jsonify({"error": "Data not found"}), 404

    except Exception as e:
        # Handle other unforeseen errors
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


def extract_key_data(req: requests.Request) -> tuple[str, str, dict[str, any]]:
    data: dict[str, any] = req.json
    uuid: str = data.get('uuid')
    name: str = data.get('name')
    is_active: bool = data.get('is_active')
    key_data: dict[str, any] = {
        "server": data.get('server'),
        "server_port": data.get('server_port'),
        "password": data.get('password'),
        "method": data.get('method'),
        "is_active": is_active
    }
    return uuid, name, key_data


@app.route("/key", methods=['POST'])
def create_key():

    try:
        # Extract key data from the request payload
        uuid, name, key_data = extract_key_data(request)

        # Check if all required fields are present
        if not all([uuid, name, key_data['server'], key_data['server_port'],
                    key_data['password'], key_data['method'], key_data['is_active']]):
            return jsonify({"error": "All fields are required"}), 400

        # Initialize database manager and create the key
        db_manager = DatabaseManager()
        db_manager.create_key(name, uuid, key_data)
        db_manager.close()

        return jsonify({"success": True, "message": "Key successfully created"}), 201

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@app.route("/key", methods=['PUT'])
def modify_key():

    try:
        # Extract key data from the request payload
        uuid, name, key_data = extract_key_data(request)

        # Check if all required fields are present
        if not all([uuid, name, key_data['server'], key_data['server_port'],
                    key_data['password'], key_data['method'], key_data['is_active'] is not None]):
            return jsonify({"error": "All fields are required"}), 400

        # Initialize database manager and modify the key
        db_manager = DatabaseManager()
        db_manager.modify_key(name, uuid, key_data)
        db_manager.close()

        return jsonify({"success": True, "message": "Key successfully modified"}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(port=FLASK_APP_PORT)
