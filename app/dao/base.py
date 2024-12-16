from app.utils.database import create_connection, create_connection_users
import psycopg2


class BaseDAO:

    table = None

    @classmethod
    def fetch_data(cls):
        connection = create_connection()
        cursor = connection.cursor()
        try:
            query = f"SELECT * FROM {cls.table}"
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def add_data(cls, values: tuple):
        connection = create_connection()
        cursor = connection.cursor()
        try:
            placeholders = ",".join(["%s"] * len(values))

            query = f"INSERT INTO {cls.table} VALUES (DEFAULT, {placeholders})"

            cursor.execute(query, values)
            connection.commit()
            success = True
            return success
        except Exception as e:
            error = False
            return error
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def delete_data(cls, del_id: int):
        connection = create_connection()
        cursor = connection.cursor()
        query = f"DELETE FROM {cls.table} WHERE id = %s"
        try:
            cursor.execute(query, (del_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print("Error deleting data:", str(e))
            cursor.close()
            connection.close()
            return False


    @classmethod
    def truncate_table(cls) -> None:
        connection = create_connection()
        cursor = connection.cursor()
        query = f"TRUNCATE TABLE {cls.table}"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()

    @classmethod
    def fetch_all_data(cls):
        connection = create_connection()
        cursor = connection.cursor()

        try:
            query = f"SELECT * FROM {cls.table}"
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
        finally:
            cursor.close()
            connection.close()


class BaseUserDAO:

    table = None

    @classmethod
    def fetch_all_data(cls):
        connection = create_connection_users()
        cursor = connection.cursor()

        try:
            query = f"SELECT * FROM {cls.table}"
            cursor.execute(query)
            data = cursor.fetchall()
            return data
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def fetch_req(cls, text: str):
        connection = create_connection_users()
        cursor = connection.cursor()

        try:
            query = f"SELECT * FROM {cls.table} WHERE is_approved = %s"
            values = (text,)
            cursor.execute(query, values)
            data = cursor.fetchall()
            return data
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
        finally:
            cursor.close()
            connection.close()

    @classmethod
    def approve_user(cls, username: str):
        connection = create_connection_users()
        cursor = connection.cursor()
        update_query = f"UPDATE {cls.table} SET is_approved = true WHERE username = %s"
        values = (username,)
        cursor.execute(update_query, values)
        connection.commit()
        connection.close()

    @classmethod
    def delete_user(cls, username: str) -> None:
        connection = create_connection()
        cursor = connection.cursor()
        query = f"DELETE FROM {cls.table} WHERE username = {username}"
        cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()