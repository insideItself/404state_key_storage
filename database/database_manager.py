import psycopg2
from config import POSTGRES_CREDENTIALS
# import names
import uuid


class DatabaseManager:

    def __init__(self) -> None:
        self.conn = psycopg2.connect(**POSTGRES_CREDENTIALS)
        self.conn.autocommit = True  # Set autocommit to True
        self.cursor = self.conn.cursor()

    def create_outline_server(self, hostname: str, port: int, api_url: str,
                              location_name: str, provider_id: int) -> int:
        try:
            # Start a transaction
            self.conn.autocommit = False

            # Check if provider_id exists
            provider_query: str = "SELECT 1 FROM server_provider WHERE id = %s;"
            self.cursor.execute(provider_query, (provider_id,))
            if not self.cursor.fetchone():
                raise ValueError(f"Provider with id '{provider_id}' not found")

            # Insert data into outline_server table
            insert_server_query: str = """
                INSERT INTO outline_server (hostname, port, api_url, is_active)
                VALUES (%s, %s, %s, TRUE)
                RETURNING id;
            """
            self.cursor.execute(insert_server_query, (hostname, port, api_url))
            outline_server_id: int = self.cursor.fetchone()[0]

            # Fetch location id from server_location table
            location_query: str = "SELECT id FROM server_location WHERE location = %s;"
            self.cursor.execute(location_query, (location_name,))
            location_result: tuple[int, ...] | None = self.cursor.fetchone()
            if not location_result:
                raise ValueError(f"Location '{location_name}' not found")

            location_id: int = location_result[0]

            # Insert data into outline_server_info table
            insert_server_info_query: str = """
                INSERT INTO outline_server_info (fk_outline_server_id, fk_server_location_id, fk_server_provider_id)
                VALUES (%s, %s, %s);
            """
            self.cursor.execute(insert_server_info_query, (outline_server_id, location_id, provider_id))

            # Commit the transaction
            self.conn.commit()

            # Set autocommit back to True
            self.conn.autocommit = True

            return outline_server_id
        except Exception as e:
            # Rollback the transaction in case of any exception
            self.conn.rollback()
            # Set autocommit back to True
            self.conn.autocommit = True
            raise e

    def check_server_exists_using_api_url(self, api_url: str) -> bool:
        query = "SELECT 1 FROM outline_server WHERE api_url = %s LIMIT 1;"
        self.cursor.execute(query, (api_url,))
        return self.cursor.fetchone() is not None

    def check_server_exists_using_id(self, server_id: int) -> bool:
        query = "SELECT 1 FROM outline_server WHERE id = %s LIMIT 1;"
        self.cursor.execute(query, (server_id,))
        return self.cursor.fetchone() is not None

    def get_server_api_url(self, server_id: int) -> str:
        query = "SELECT api_url FROM outline_server WHERE id = %s LIMIT 1;"
        self.cursor.execute(query, (server_id,))
        return self.cursor.fetchone()[0]

    def location_exists(self, location_name: str) -> bool:
        query = """
            SELECT 1 
            FROM server_location 
            WHERE location = %s 
            LIMIT 1;
        """
        self.cursor.execute(query, (location_name,))
        return self.cursor.fetchone() is not None

    def get_servers(self, location_name: str | None = None) -> dict[str, any]:
        try:
            query = """
                SELECT os.id, sl.location, COUNT(ok.id) AS unused_keys
                FROM outline_server os
                JOIN outline_server_info osi ON os.id = osi.fk_outline_server_id
                JOIN server_location sl ON osi.fk_server_location_id = sl.id
                LEFT JOIN outline_key ok ON os.id = ok.fk_outline_server_id AND ok.currently_used = FALSE
                WHERE os.is_active = TRUE
            """

            params = []
            if location_name is not None:
                query += " AND sl.location = %s"
                params.append(location_name)

            query += " GROUP BY os.id, sl.location"
            self.cursor.execute(query, params)

            servers = [{"id": row[0], "location": row[1], "unused_keys": row[2]} for row in self.cursor.fetchall()]
            total_count = len(servers)

            return {"total_count": total_count, "servers": servers}

        except Exception as e:
            self.conn.rollback()
            raise e

    def generate_unique_uuid(self) -> str:
        while True:
            new_uuid = str(uuid.uuid4())
            if not self.check_uuid_exists(new_uuid):
                return new_uuid

    def check_uuid_exists(self, new_uuid: str) -> bool:
        query = "SELECT 1 FROM outline_key WHERE uuid = %s LIMIT 1;"
        self.cursor.execute(query, (new_uuid,))
        return self.cursor.fetchone() is not None

    def insert_key(self, uuid: str, id: str, fk_outline_server_id: int, access_url: str, currently_used: bool) -> None:
        query = """
            INSERT INTO outline_key (uuid, id, fk_outline_server_id, access_url, currently_used)
            VALUES (%s, %s, %s, %s, %s);
        """
        self.cursor.execute(query, (uuid, id, fk_outline_server_id, access_url, currently_used))

    def get_outline_keys(self, server_id: int, currently_used: bool | None = None,
                         limit: int | None = None) -> list[dict[str, any]]:
        try:
            query: str = """
                SELECT uuid, access_url, currently_used 
                FROM outline_key 
                WHERE fk_outline_server_id = %s
            """
            params: list[int] = [server_id]

            if currently_used is not None:
                query += " AND currently_used = %s"
                params.append(currently_used)

            if limit is not None:
                query += " LIMIT %s"
                params.append(limit)

            self.cursor.execute(query, params)
            keys: list[dict[str, any]] = [
                {"uuid": row[0], "access_url": row[1], "currently_used": row[2]} for row in self.cursor.fetchall()
            ]

            return keys
        except Exception as e:
            # self.conn.rollback()
            raise e

    def get_locations(self, active_servers: bool | None = None) -> list[dict[str, str]]:
        try:
            if active_servers is True:
                # Fetch locations with active servers
                query = """
                    SELECT DISTINCT sl.location, sl.location_ru, sl.iso
                    FROM server_location sl
                    INNER JOIN outline_server_info osi ON sl.id = osi.fk_server_location_id
                    INNER JOIN outline_server os ON osi.fk_outline_server_id = os.id
                    WHERE os.is_active = TRUE;
                """
            elif active_servers is False:
                # Fetch locations without active servers
                query = """
                    SELECT sl.location, sl.location_ru, sl.iso
                    FROM server_location sl
                    WHERE NOT EXISTS (
                        SELECT 1 FROM outline_server_info osi
                        INNER JOIN outline_server os ON osi.fk_outline_server_id = os.id
                        WHERE osi.fk_server_location_id = sl.id AND os.is_active = TRUE
                    );
                """
            else:
                # Fetch all locations
                query = "SELECT sl.location, sl.location_ru, sl.iso FROM server_location sl;"

            self.cursor.execute(query)
            return [{"location": row[0], "location_ru": row[1], "iso": row[2]} for row in self.cursor.fetchall()]
        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self) -> None:
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":

    # db_manager = DatabaseManager()

    ...
