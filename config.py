import os

"""
This code first checks whether the DOCKER_CONTAINER environment variable is set.
If it’s not set (i.e., None), it means that the code is not running inside a Docker container.
In this case, the load_dotenv() function is called to load the environment variables from the .env file.
"""

# Check if running inside a Docker container
running_in_docker = os.environ.get('DOCKER_CONTAINER') is not None

# Load environment variables from .env file if not running in Docker
if not running_in_docker:
    from dotenv import load_dotenv
    load_dotenv()

FLASK_APP_PORT: int = int(os.getenv("FLASK_APP_PORT"))

# Conditionally set PostgreSQL hostname and port
if running_in_docker:
    POSTGRES_HOSTNAME = os.environ.get("POSTGRES_CONTAINER_HOSTNAME")
    POSTGRES_PORT = os.environ.get("POSTGRES_CONTAINER_PORT")
else:
    POSTGRES_HOSTNAME = os.environ.get("POSTGRES_HOSTNAME")
    POSTGRES_PORT = os.environ.get("POSTGRES_PORT")

POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USERNAME: str = os.getenv("POSTGRES_USERNAME")
POSTGRES_DATABASE: str = os.getenv("POSTGRES_DATABASE")

POSTGRES_CREDENTIALS: dict[str, str] = {
    "dbname": POSTGRES_DATABASE,
    "user": POSTGRES_USERNAME,
    "password": POSTGRES_PASSWORD,
    "host": POSTGRES_HOSTNAME,
    "port": POSTGRES_PORT
}