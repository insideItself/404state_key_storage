import requests
from requests.exceptions import RequestException
from flask import Blueprint, jsonify, request, Response
from database.database_manager import DatabaseManager
import urllib3
# from urllib.parse import urlparse
import uuid
from config import auth

outline_keys_bp = Blueprint('outline_keys', __name__)


@outline_keys_bp.route("/outline_keys/<int:outline_server_id>", methods=['GET'])
@auth.login_required
def get_outline_keys(outline_server_id: int) -> tuple[Response, int]:

    db_manager: DatabaseManager = DatabaseManager()

    try:
        if not db_manager.check_server_exists_using_id(outline_server_id):
            return jsonify({"error": "Server not found"}), 404

        # Validate 'currently_used' parameter
        currently_used_query = request.args.get('currently_used')
        currently_used: bool | None = None
        if currently_used_query is not None:
            if currently_used_query.lower() in ['true', 'false']:
                currently_used = currently_used_query.lower() == 'true'
            else:
                return jsonify({"error": "Invalid 'currently_used' parameter. It must be 'true' or 'false'."}), 400

        # Validate 'limit' parameter
        limit_query = request.args.get('limit')
        limit: int | None = None
        if limit_query is not None:
            if limit_query.isdigit() and int(limit_query) > 0:
                limit = int(limit_query)
            else:
                return jsonify({"error": "Invalid 'limit' parameter. It must be a positive integer."}), 400

        keys: list[dict[str, any]] = db_manager.get_outline_keys(outline_server_id, currently_used, limit)
        total_keys_count = len(keys)

        return jsonify({"total_count": total_keys_count, "keys": keys}), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
    finally:
        db_manager.close()


@outline_keys_bp.route("/outline_keys", methods=['POST'])
@auth.login_required
def create_outline_keys() -> tuple[Response, int]:

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    db_manager: DatabaseManager = DatabaseManager()
    keys_created: list[dict[str, uuid.uuid4]] = []
    keys_failed: list[dict[str, str]] = []

    try:
        data: dict = request.get_json()

        # Check if all required parameters are presented in request body
        required_keys: set[str] = {"outline_server_id", "number_of_keys"}
        missing_keys = [key for key in required_keys if key not in data]

        # Return 400 error if some of the parameters are missing
        if missing_keys:
            missing_keys_str = ', '.join(missing_keys)
            return jsonify({"error": f"Missing required parameters: {missing_keys_str}"}), 400

        # Validate that both parameters are integers
        outline_server_id = data.get("outline_server_id")
        number_of_keys = data.get("number_of_keys")
        if not isinstance(outline_server_id, int) or not isinstance(number_of_keys, int):
            return jsonify({"error": "Both outline_server_id and number_of_keys must be integers"}), 400

        # Ensure number_of_keys is not zero
        if number_of_keys == 0:
            return jsonify({"error": "number_of_keys cannot be zero"}), 400

        # Check if server exists
        # db_manager: DatabaseManager = DatabaseManager()
        server_id: int = data.get("outline_server_id")

        if not db_manager.check_server_exists_using_id(server_id):
            db_manager.close()  # Ensure the database connection is closed
            return jsonify({"error": "Server not found"}), 404

        # db_manager.close()

        api_url: str = db_manager.get_server_api_url(server_id)

        # Key creation logic
        for _ in range(number_of_keys):
            unique_uuid: uuid.uuid4 = db_manager.generate_unique_uuid()
            try:

                # Specify the timeout duration (e.g., 3 seconds)
                timeout_duration = 2

                post_response: requests.Response = requests.post(
                    f"{api_url}/access-keys",
                    verify=False,
                    timeout=timeout_duration
                )

                post_response.raise_for_status()
                key_data = post_response.json()
                key_id: str = key_data['id']
                access_url: str = key_data['accessUrl']

                # Set the name for the key
                put_response: requests.Response = requests.put(
                    f"{api_url}/access-keys/{key_id}/name",
                    json={"name": f"shadowtrail:{unique_uuid}"},
                    verify=False
                )
                put_response.raise_for_status()

                # Insert key data into database
                db_manager.insert_key(unique_uuid, key_id, server_id, access_url, False)
                keys_created.append({"uuid": unique_uuid})

            except requests.exceptions.Timeout:
                # Handle the timeout case
                keys_failed.append({"uuid": unique_uuid, "error": "Request timed out"})

            except RequestException as e:
                keys_failed.append({"uuid": unique_uuid, "error": str(e)})

        db_manager.close()

        # Check if all key creation attempts have failed
        if not keys_created and keys_failed:
            return jsonify(
                {"error": "All key creation attempts failed", "details": [key["error"] for key in keys_failed]}), 422

        response_data: dict[str, any] = {
            "total_success": len(keys_created),
            "successful_keys": keys_created,
            "total_failed": len(keys_failed),
            "failed_keys": keys_failed
        }

        status_code: int = 201 if not keys_failed else 207  # HTTP 207 Multi-Status might be appropriate here

        return jsonify(response_data), status_code

    except Exception as e:
        db_manager.close()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
