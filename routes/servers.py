import requests
from requests.exceptions import RequestException
from flask import Blueprint, jsonify, request, Response
from database.database_manager import DatabaseManager
import urllib3
from urllib.parse import urlparse
from config import auth

servers_bp = Blueprint('servers', __name__)


@servers_bp.route("/servers", methods=['GET'])
@auth.login_required
def get_outline_servers() -> tuple[Response, int]:

    db_manager: DatabaseManager = DatabaseManager()

    try:
        location_name: str | None = request.args.get('location', default=None, type=str)

        if location_name is not None and not db_manager.location_exists(location_name):
            db_manager.close()
            return jsonify({"error": "Location not found"}), 404

        servers_info: dict[str, any] = db_manager.get_servers(location_name)
        db_manager.close()
        return jsonify(servers_info), 200

    except Exception as e:
        db_manager.close()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@servers_bp.route("/servers", methods=['POST'])
@auth.login_required
def create_outline_server() -> tuple[Response, int]:
    # suppress warning about self-signed certificate on an outline server
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        data: dict = request.get_json()

        # check if all required parameters are presented in request body
        required_keys: set[str] = {"api_url", "location", "provider_id"}
        missing_keys: list | None = [key for key in required_keys if key not in data]

        # return 400 error if some of the parameters is missing
        if missing_keys:
            missing_keys_str = ', '.join(missing_keys)
            return jsonify({"error": f"Missing required parameters: {missing_keys_str}"}), 400

        # validate provider_id as a positive integer
        provider_id: any = data.get("provider_id")
        if not isinstance(provider_id, int) or provider_id <= 0:
            return jsonify({"error": "Invalid provider_id. It must be a positive integer"}), 404

        # check if server exists
        api_url: str = data.get("api_url")
        parsed_url = urlparse(api_url)

        # check if URL scheme is valid
        if parsed_url.scheme not in ['http', 'https']:
            return jsonify({"error": "Invalid URL scheme"}), 422

        # if requests package throws error, return 500 error with error details
        try:
            response: requests.Response = requests.get(f"{api_url}/server", verify=False)
        except RequestException as e:
            # This will catch any RequestException, which includes exceptions like ConnectionError,
            # HTTPError, Timeout, TooManyRedirects which are raised for failed requests.
            # Return a 500 error for these unexpected issues.
            return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

        # if we get anything except 200 response, return 404 error
        if response.status_code != 200:
            return jsonify({"error": "Server was found but unexpected error occurred"}), 404

        # main logic
        db_manager: DatabaseManager = DatabaseManager()
        response_data: dict = response.json()

        # Check if a server with the provided api_url already exists
        if db_manager.check_server_exists_using_api_url(api_url):
            db_manager.close()  # Ensure the database connection is closed
            return jsonify({"error": "Server with provided api_url already exists in database"}), 409

        # try to insert data into database, if everything ok - return 201 response code and row identifier in database
        # if some error occurred - return 500 and error details
        try:

            db_manager: DatabaseManager = DatabaseManager()
            outline_server_id: int = db_manager.create_outline_server(
                hostname=response_data.get("hostnameForAccessKeys"),
                port=response_data.get("portForNewAccessKeys"),
                api_url=data.get('api_url'),
                location_name=data.get('location'),
                provider_id=data.get('provider_id')
            )

        except Exception as e:
            db_manager.close()
            return jsonify({"error": "Failed to create outline server", "details": str(e)}), 500

        db_manager.close()  # Ensure the database connection is closed

        return jsonify({"id": outline_server_id}), 201

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
