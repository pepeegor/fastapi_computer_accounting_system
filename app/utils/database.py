import psycopg2


def create_connection():
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="computer_accounting_system",
        user="postgres",
        password="123"
    )
    return connection


def create_connection_users():
    connection = psycopg2.connect(
        host="localhost",
        port="5432",
        database="users",
        user="postgres",
        password="123"
    )
    return connection
