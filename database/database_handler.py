import sqlite3

CONNECTION_STRING = "BR_DB"


def get_all_recommended_books_for_user(user_name):
    user_name = user_name.lower()
    user = get_user(user_name)
    query = "SELECT Book.Name FROM (SELECT * FROM Recommendation WHERE User_id = {}) AS Recommendation INNER JOIN " \
            "Book ON Book.Id = Recommendation.Book_id".format(user[0])
    result = execute_query_with_result(query)
    return result


def get_recommended_book(user_name, book_name):
    user_name = user_name.lower()
    book_name = book_name.lower()
    book = get_book(book_name)
    user = get_user(user_name)
    query = "SELECT * FROM Recommendation WHERE User_id = '{}' AND Book_id = '{}'".format(user[0], book[0])
    result = execute_query_with_result(query)
    if len(result) == 0:
        return None
    return result[0]


def add_recommended_book(user_name, book_name):
    user_name = user_name.lower()
    book_name = book_name.lower()
    book = get_book(book_name)
    user = get_user(user_name)
    recommendation = get_recommended_book(user_name, book_name)
    if recommendation is None:
        query = "INSERT INTO Recommendation (User_id, Book_id, Amount) VALUES ({}, {}, 0)".format(user[0], book[0])
        if book is None:
            create_book(book_name, 0)
        if user is None:
            create_user(user_name)
    else:
        query = "UPDATE Recommendation SET Amount = Amount + 1 WHERE User_id = '{}' AND Book_id = '{}'"\
            .format(user[0], book[0])
    execute_query_without_result(query)


def get_user(user_name):
    user_name = user_name.lower()
    parameters = (user_name, )
    query = "SELECT * FROM User WHERE Name = ?"
    result = execute_query_with_result(query, parameters)
    if len(result) == 0:
        return None
    return result[0]


def get_user_by_id(user_id):
    query = "SELECT * FROM User WHERE Id = {}".format(user_id)
    result = execute_query_with_result(query)
    if len(result) == 0:
        return None
    return result[0]


def create_user(user_name):
    user_name = user_name.lower()
    if get_user(user_name) is not None:
        return
    parameters = (user_name, )
    query = "INSERT INTO User (Name) VALUES (?)"
    execute_query_without_result(query, parameters)


def get_book(book_name):
    book_name = book_name.replace("'", "''").lower()
    query = "SELECT * FROM Book WHERE Name = '{}'".format(book_name)
    result = execute_query_with_result(query)
    if len(result) != 0:
        return result[0]
    return None


def create_book(book_name, genre_id):
    book_name = book_name.lower()
    parameters = (book_name, genre_id)
    book = get_book(book_name)
    if book is None:
        query = "INSERT INTO Book (Name, Genre_id) VALUES(?, ?)"
        execute_query_without_result(query, parameters)
        return get_book(book_name)
    return book


def register_hit(hit_id, user_name, requested_genre, requested_book, verification=False, verification_required=False):
    user = get_user(user_name)
    requested_book = requested_book.replace("'", "''").lower()
    query = "INSERT INTO Hit (Id, User_id, Verification, Requested_genre, Requested_book, Verification_required) " \
            "VALUES ('{}', {}, {}, '{}', '{}', {})".format(hit_id, user[0], verification, requested_genre,
                                                           requested_book, verification_required)
    print(query)
    execute_query_without_result(query)


def get_hit(user_name):
    user = get_user(user_name)
    query = "SELECT * FROM Hit WHERE User_id = {}".format(user[0])
    result = execute_query_with_result(query)
    if len(result) == 0:
        return None
    return result[0]


def get_all_hits(verification=False, verification_required=False):
    query = "SELECT * FROM Hit WHERE VERIFICATION=".format(verification)
    if not verification:
        query += " AND Verification_required = {}".format(verification_required)
    result = execute_query_with_result(query)
    if len(result) == 0:
        return None
    return result


def delete_hit(user_name, verification=False):
    user = get_user(user_name)
    parameters = (user[0], verification)
    query = "DELETE FROM Hit WHERE User_id = ? AND Verification = ?"
    execute_query_without_result(query, parameters)


def add_read_book(user_name, book_name, genre, rating):
    user = get_user(user_name)
    genre = create_genre(genre)
    book = create_book(book_name, genre[0])
    if book[0] not in get_read_books(user_name):
        query = "INSERT INTO User_Book (User_id, Book_id, Rating, Genre_id) VALUES ({}, {}, {}, {})"\
            .format(user[0], book[0], rating, genre[0])
    else:
        query = "UPDATE User_Book SET Rating = {} WHERE User_id = {} AND Book_id = {}".format(rating, user[0], book[0])
    execute_query_without_result(query)


def get_read_books(user_name):
    user = get_user(user_name)
    query = "SELECT Book.Name, Rating FROM User_Book INNER JOIN Book on Book.Id = User_Book.Book_id WHERE User_id = {}"\
        .format(user[0])
    result = execute_query_with_result(query)
    print(result)
    if len(result) == 0:
        return []
    return result


def get_genre(genre_name):
    genre_name = genre_name.lower()
    parameters = (genre_name, )
    query = "SELECT * FROM Genre WHERE Name = ?"
    result = execute_query_with_result(query, parameters)
    if len(result) == 0:
        return None
    return result[0]


def create_genre(genre_name):
    genre_name = genre_name.lower()
    parameters = (genre_name, )
    genre = get_genre(genre_name)
    if not genre:
        query = "INSERT INTO Genre (Name) VALUES (?) RETURNING *"
        return execute_query_with_result(query, parameters)[0]
    return genre[0]


def execute_query_with_result(query, parameters=None):
    connection = create_connection()
    cursor = connection.cursor()
    if parameters:
        result = cursor.execute(query, parameters).fetchall()
    else:
        result = cursor.execute(query).fetchall()
    connection.close()
    return result


def execute_query_without_result(query, parameters=None):
    connection = create_connection()
    cursor = connection.cursor()
    if parameters:
        cursor.execute(query, parameters)
    else:
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
                            "Rating INTEGER NOT NULL,"
                            "Genre_id INTEGER NOT NULL)")

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
                            "Book_id INTEGER NOT NULL,"
                            "Amount INTEGER NOT NULL)")

    tables_to_create.append("CREATE TABLE IF NOT EXISTS Hit ("
                            "Id INTEGER NOT NULL,"
                            "User_id INTEGER NOT NULL,"
                            "Verification BOOLEAN NOT NULL,"
                            "Requested_genre VARCHAR(64) NOT NULL,"
                            "Requested_book VARCHAR(64) NOT NULL,"
                            "Verification_required BOOLEAN NOT NULL)")

    for table_query in tables_to_create:
        cur.execute(table_query)
    connection.commit()
    connection.close()
