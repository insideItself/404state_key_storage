import requests
from requests.exceptions import RequestException
from flask import Blueprint, jsonify, request, Response
from database.database_manager import DatabaseManager
from flask_cors import cross_origin
# import urllib3
# from urllib.parse import urlparse
import uuid
from config import auth

dynamic_keys_bp = Blueprint('dynamic_keys', __name__)


@dynamic_keys_bp.route("/keys/<int:key_id>", methods=['GET'])
@cross_origin()  # turn on CORS to make this endpoint available from Outline Client
def get_dynamic_key(key_id) -> tuple[Response, int]:
    db_manager = DatabaseManager()
    tg_user_id = request.args.get('tg_user_id', type=int)

    if not tg_user_id:
        return jsonify({"error": "Both key_id and tg_user_id are required"}), 400

    try:
        key_details = db_manager.get_dynamic_key_details(key_id, tg_user_id)
        if not key_details:
            return jsonify({"error": "Key not found or inactive"}), 404

        return jsonify(key_details), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        db_manager.close()


@dynamic_keys_bp.route("/keys", methods=['POST'])
@auth.login_required
def create_dynamic_key() -> tuple[Response, int]:

    # urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    db_manager = DatabaseManager()

    try:
        data = request.get_json()
        required_keys = {"tg_user_id", "outline_key_uuid"}
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            return jsonify({"error": f"Missing required parameters: {', '.join(missing_keys)}"}), 400

        tg_user_id, outline_key_uuid = data.get("tg_user_id"), data.get("outline_key_uuid")
        if not db_manager.check_outline_key_exists(outline_key_uuid):
            return jsonify({"error": "Outline key uuid not found"}), 404

        # Check if dynamic key already exists for the user
        if db_manager.check_dynamic_key_exists_for_user(tg_user_id):
            return jsonify(
                {"error": "Dynamic key with provided tg_user_id already exists in database"}), 409

        unique_id = db_manager.generate_unique_dynamic_key_id()
        access_url = db_manager.get_access_url_by_outline_key(outline_key_uuid)
        key_details = db_manager.parse_access_url(access_url)

        # Insert data into dynamic_key table
        db_manager.insert_dynamic_key(
            unique_id,
            tg_user_id,
            key_details["server"],
            key_details["server_port"],
            key_details["password"],
            key_details["method"],
            True,
            outline_key_uuid
        )

        return jsonify({"id": unique_id}), 201

    except RequestException as e:
        return jsonify({"error": "Failed to create dynamic key", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        db_manager.close()


@dynamic_keys_bp.route("/keys/<int:key_id>", methods=['PATCH'])
@auth.login_required
def patch_dynamic_key(key_id) -> tuple[Response, int]:

    db_manager = DatabaseManager()

    try:
        # Check if dynamic key exists
        if not db_manager.check_dynamic_key_exists_by_id(key_id):
            return jsonify({"error": "Dynamic key not found"}), 404

        # Update the dynamic key and the associated outline key
        db_manager.deactivate_dynamic_key_and_outline_key(key_id)

        return jsonify({"message": "Dynamic key and associated outline key updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        db_manager.close()


@dynamic_keys_bp.route("/keys/<int:key_id>", methods=['PUT'])
@auth.login_required
def modify_dynamic_key(key_id) -> tuple[Response, int]:
    db_manager = DatabaseManager()

    try:
        data = request.get_json()
        if "outline_key_uuid" not in data:
            return jsonify({"error": "Missing required parameter: 'outline_key_uuid'"}), 400

        outline_key_uuid = data["outline_key_uuid"]
        if not db_manager.check_outline_key_exists(outline_key_uuid):
            return jsonify({"error": "Outline key uuid not found"}), 404

        if not db_manager.check_dynamic_key_exists_by_id(key_id):
            return jsonify({"error": "Dynamic key not found"}), 404

        # Extract details from access_url for the new outline key
        access_url = db_manager.get_access_url_by_outline_key(outline_key_uuid)
        key_details = db_manager.parse_access_url(access_url)

        # Update the dynamic key and associated outline key
        db_manager.update_dynamic_key_with_new_outline_key(key_id, outline_key_uuid, key_details)

        return jsonify({"message": "Dynamic key and associated outline key updated successfully"}), 200

    except RequestException as e:
        return jsonify({"error": "Failed to update dynamic key", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        db_manager.close()
