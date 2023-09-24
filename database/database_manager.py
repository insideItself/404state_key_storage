import psycopg2
from config import POSTGRES_CREDENTIALS
# import names


class DatabaseManager:

    def __init__(self) -> None:
        self.conn = psycopg2.connect(**POSTGRES_CREDENTIALS)
        self.cursor = self.conn.cursor()

    def get_key_by_uuid(self, name: str, uuid: str) -> dict[str, any]:
        query = "SELECT hostname, port, password, method FROM keys WHERE name = %s AND uuid = %s;"
        self.cursor.execute(query, (name, uuid))
        result: tuple[str, int, str, str] = self.cursor.fetchone()

        key_data: dict[str, any] = {
            "server": result[0],
            "server_port": result[1],
            "password": result[2],
            "method": result[3]
        }

        return key_data

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    # print(uuid4())
    # print(POSTGRES_CREDENTIALS)
    db_manager = DatabaseManager()
    data = db_manager.get_key_by_uuid('aileen', '2b78210a-5fe9-4ed5-b8fe-2e78e2b867d2')
    print(data)
    db_manager.close()
    # print(names.get_first_name(gender='female'))
