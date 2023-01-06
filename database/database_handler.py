import sqlite3

CONNECTION_STRING = "BR_DB"


def execute_query_without_result(query):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()


def execute_query_with_result(query):
    connection = create_connection()
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    return result


def create_connection():
    return sqlite3.connect(CONNECTION_STRING)


def create_db():
    connection = create_connection()
    cur = connection.cursor()
    tables_to_create = []

    tables_to_create.append("CREATE TABLE IF NOT EXISTS User ("
                            "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "Name VARCHAR(64) NOT NULL,"
                            "Password VARCHAR(64) NOT NULL)")

    tables_to_create.append("CREATE TABLE IF NOT EXISTS User_Book ("
                            "User_id INTEGER NOT NULL,"
                            "Book_id INTEGER NOT NULL,"
                            "Rating INTEGER NOT NULL)")

    tables_to_create.append("CREATE TABLE IF NOT EXISTS User_Genre ("
                            "User_id INTEGER NOT NULL,"
                            "Genre_id INTEGER NOT NULL)")

    tables_to_create.append("CREATE TABLE IF NOT EXISTS Book ("
                            "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "Name VARCHAR(128) NOT NULL,"
                            "Genre_id INTEGER NOT NULL)")

    tables_to_create.append("CREATE TABLE IF NOT EXISTS Genre ("
                            "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "Name VARCHAR(64) NOT NULL)")

    for table_query in tables_to_create:
        cur.execute(table_query)
    connection.commit()
    connection.close()
