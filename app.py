from flask import Flask
from config import FLASK_APP_PORT
import socket
from routes.servers import servers_bp
from routes.outline_keys import outline_keys_bp
from routes.dynamic_keys import dynamic_keys_bp
from routes.locations import locations_bp
from routes.swagger import swagger_bp

app = Flask(__name__)

# app.register_blueprint(swagger_bp)
app.register_blueprint(servers_bp)
app.register_blueprint(outline_keys_bp)
app.register_blueprint(dynamic_keys_bp)
app.register_blueprint(locations_bp)

# Register the Swagger UI blueprint
# app.register_blueprint(swagger_bp)


# @app.route("/")
# def return_key():
#     return f"Container ID: {socket.gethostname()}"


if __name__ == "__main__":
    app.run(port=FLASK_APP_PORT)
