import os

"""
This code first checks whether the DOCKER_CONTAINER environment variable is set.
If it’s not set (i.e., None), it means that the code is not running inside a Docker container.
In this case, the load_dotenv() function is called to load the environment variables from the .env file.
"""

if os.environ.get('DOCKER_CONTAINER') is None:
    from dotenv import load_dotenv
    load_dotenv()

FLASK_APP_PORT: int = int(os.getenv("FLASK_APP_PORT"))

POSTGRES_HOST: str = os.getenv("POSTGRES_HOST") if os.getenv("POSTGRES_HOST") is not None else "localhost"
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD")
POSTGRES_USERNAME: str = os.getenv("POSTGRES_USERNAME")
POSTGRES_DATABASE: str = os.getenv("POSTGRES_DATABASE")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT")

POSTGRES_CREDENTIALS: dict[str, str] = {
    "dbname": POSTGRES_DATABASE,
    "user": POSTGRES_USERNAME,
    "password": POSTGRES_PASSWORD,
    "host": POSTGRES_HOST,
    "port": POSTGRES_PORT
}
