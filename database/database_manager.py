import psycopg2
from config import POSTGRES_CREDENTIALS
# import names
# from uuid import uuid4


class DatabaseManager:

    def __init__(self) -> None:
        self.conn = psycopg2.connect(**POSTGRES_CREDENTIALS)
        self.cursor = self.conn.cursor()

    def get_key(self, name: str, uuid: str) -> dict[str, any]:
        query = "SELECT server, server_port, password, method FROM keys " \
                "WHERE name = %s AND uuid = %s and is_active = True;"
        self.cursor.execute(query, (name, uuid))
        result: tuple[str, int, str, str] = self.cursor.fetchone()

        key_data: dict[str, any] = {
            "server": result[0],
            "server_port": result[1],
            "password": result[2],
            "method": result[3]
        }

        return key_data

    def create_key(self, name: str, uuid: str, key_data: dict[str, any]) -> None:
        query = """INSERT INTO keys (uuid, server, server_port, password, method, name, is_active)
                   VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        self.cursor.execute(query, (uuid, key_data.get('server'), key_data.get('server_port'),
                                    key_data.get('password'), key_data.get('method'), name, key_data.get('is_active'))
                            )
        self.conn.commit()

    def modify_key(self, name: str, uuid: str, key_data: dict[str, any]) -> None:
        query = """UPDATE keys SET 
                   server = %s, 
                   server_port = %s, 
                   password = %s, 
                   method = %s,
                   is_active = %s
                   WHERE uuid = %s AND name = %s;"""
        self.cursor.execute(query, (key_data.get('server'), key_data.get('server_port'),
                                    key_data.get('password'), key_data.get('method'), key_data.get('is_active'),
                                    uuid, name)
                            )
        self.conn.commit()

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":

    key_data_: dict[str, any] = {
        "server": '0.0.0.0',
        "server_port": '0000',
        "password": 'test_pass',
        "method": 'chacha20-ietf-poly1305',
        "is_active": False
    }

    # db_manager = DatabaseManager()
    # data = db_manager.get_key('aileen', '2b78210a-5fe9-4ed5-b8fe-2e78e2b867d2')
    # print(data)
    # db_manager.modify_key('aileen', '2b78210a-5fe9-4ed5-b8fe-2e78e2b867d2', key_data_)
    # db_manager.create_key('jane', str(uuid4()), key_data_)
    # db_manager.modify_key('aileen', '2b78210a-5fe9-4ed5-b8fe-2e78e2b867d2', key_data_)
    # db_manager.close()
    # print(names.get_first_name(gender='female'))
