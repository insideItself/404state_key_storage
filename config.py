import os

"""
This code first checks whether the DOCKER_CONTAINER environment variable is set.
If it’s not set (i.e., None), it means that the code is not running inside a Docker container.
In this case, the load_dotenv() function is called to load the environment variables from the .env file.
"""

if os.environ.get('DOCKER_CONTAINER') is None:
    from dotenv import load_dotenv
    load_dotenv()

SERVER: str = os.getenv("SERVER")
SERVER_PORT: int = int(os.getenv("SERVER_PORT"))
PASSWORD: str = os.getenv("PASSWORD")
