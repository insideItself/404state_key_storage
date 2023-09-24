import psycopg2
import os
from config import POSTGRES_CREDENTIALS
from uuid import uuid4


class DatabaseManager:

    def __init__(self) -> None:
        self.conn = psycopg2.connect(**POSTGRES_CREDENTIALS)
        self.cursor = self.conn.cursor()


if __name__ == "__main__":
    # print(uuid4())
    # print(POSTGRES_CREDENTIALS)
    db_manager = DatabaseManager()
