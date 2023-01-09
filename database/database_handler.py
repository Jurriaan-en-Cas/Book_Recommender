import sqlite3

CONNECTION_STRING = "BR_DB"


def get_all_recommended_books_for_user(user_name):
    user = get_user(user_name)
    query = "SELECT * FROM (SELECT * FROM Recommendation WHERE User_id = {}) AS Recommendation INNER JOIN " \
            "Book ON Book.Id = Recommendation.Book_id".format(user[0])
    print(query)
    result = execute_query_with_result(query)
    return result


def add_recommended_book(user_name, book_name):
    book = get_book(book_name)
    user = get_user(user_name)
    print(user[0])
    query = "INSERT INTO Recommendation (User_id, Book_id) VALUES ({}, {})".format(user[0], book[0])
    if book is None:
        create_book(book_name, 0)
    if user is None:
        create_user(user_name)
    execute_query_without_result(query)


def get_user(user_name):
    query = "SELECT * FROM User WHERE Name = '{}'".format(user_name)
    return execute_query_with_result(query)[0]


def create_user(user_name):
    query = "INSERT INTO User (Name) VALUES ('{}')".format(user_name)
    execute_query_without_result(query)


def get_book(book_name):
    query = "SELECT * FROM Book WHERE Name = '{}'".format(book_name)
    return execute_query_with_result(query)[0]


def create_book(book_name, genre_id):
    query = "INSERT INTO Book (Name, Genre_id) VALUES('{}', {})".format(book_name, genre_id)
    execute_query_without_result(query)


def register_hit(id, user_name):
    user = get_user(user_name)
    query = "INSERT INTO Hit (Id, User_id) VALUES ('{}', {})".format(id, user[0])
    execute_query_without_result(query)


def get_hit(user_name):
    user = get_user(user_name)
    query = "SELECT * FROM Hit WHERE User_id = {}".format(user[0])
    return execute_query_with_result(query)[0]


def delete_hit(user_name):
    user = get_user(user_name)
    query = "DELETE FROM Hit WHERE User_id = {}".format(user[0])
    execute_query_without_result(query)


def execute_query_with_result(query):
    connection = create_connection()
    cursor = connection.cursor()
    result = cursor.execute(query).fetchall()
    connection.close()
    return result


def execute_query_without_result(query):
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()


def create_connection():
    return sqlite3.connect(CONNECTION_STRING)


def create_db():
    connection = create_connection()
    cur = connection.cursor()
    tables_to_create = []

    tables_to_create.append("CREATE TABLE IF NOT EXISTS 'User' ("
                            "Id INTEGER PRIMARY KEY AUTOINCREMENT,"
                            "Name VARCHAR(64) NOT NULL)")

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

    tables_to_create.append("CREATE TABLE IF NOT EXISTS Recommendation ("
                            "User_id INTEGER NOT NULL,"
                            "Book_id INTEGER NOT NULL)")

    tables_to_create.append("CREATE TABLE IF NOT EXISTS Hit ("
                            "Id INTEGER NOT NULL,"
                            "User_id INTEGER NOT NULL)")

    for table_query in tables_to_create:
        cur.execute(table_query)
    connection.commit()
    connection.close()
