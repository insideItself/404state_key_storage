from flask_swagger_ui import get_swaggerui_blueprint
from flask import Blueprint

SWAGGER_URL: str = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL: str = '/static/api.yml'  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swagger_bp: Blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "ShadowTrail VPN Key Storage API"
    },
    # oauth_config={  # OAuth config. See https://github.com/swagger-api/swagger-ui#oauth2-configuration .
    #    'clientId': "your-client-id",
    #    'clientSecret': "your-client-secret-if-required",
    #    'realm': "your-realms",
    #    'appName': "your-app-name",
    #    'scopeSeparator': " ",
    #    'additionalQueryStringParams': {'test': "hello"}
    # }
)
