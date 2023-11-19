from flask_swagger_ui import get_swaggerui_blueprint
from flask import Blueprint, redirect, url_for
from config import auth


API_URL: str = '/static/api.yml'
SWAGGER_URL: str = '/api/docs'

# Call factory function to create our blueprint
swagger_bp: Blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "ShadowTrail VPN Key Storage API"
    }
)


# Apply authentication to all routes in the blueprint
@swagger_bp.before_request
@auth.login_required
def before_request():
    # This will require authentication for every route in the blueprint
    pass