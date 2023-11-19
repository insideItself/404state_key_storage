from flask import Blueprint, jsonify, request, Response, current_app
from database.database_manager import DatabaseManager
# from app import auth
from config import auth

locations_bp = Blueprint('locations', __name__)


@locations_bp.route("/locations", methods=['GET'])
@auth.login_required
def get_locations() -> tuple[Response, int]:

    db_manager: DatabaseManager = DatabaseManager()

    try:
        # Retrieve the query parameter as a string
        active_servers_str: str | None = request.args.get('active_servers', default=None, type=str)

        # Convert the string to a boolean value, or None if it's not provided
        active_servers: bool | None = None
        if active_servers_str is not None:
            active_servers = active_servers_str.lower() == 'true'

        locations = db_manager.get_locations(active_servers)
        total_count = len(locations)

        return jsonify({"total_count": total_count, "locations": locations}), 200

    except Exception as e:
        db_manager.close()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
