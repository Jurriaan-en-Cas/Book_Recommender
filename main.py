import atexit

from flask import Flask, request, jsonify

import database.database_handler
import mTurk_interface.mTurk
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

REQUIRE_VERIFICATION = False

@app.route("/")
def hello():
    return "Welcome to the Book Recommender Python API"


@app.route("/recommend", methods=['POST'])
def recommend():
    if request.json:
        mTurk_interface.mTurk.create_recommendation(request.json['username'], request.json['genre'], request.json['book'],
                                                    REQUIRE_VERIFICATION)
        return 'OK', 200
    else:
        return 'Data is invalid.', 400


@app.route("/get_recommendations", methods=['GET'])
def get_recommendation():
    if not request.json:
        return 'Data is invalid.', 400
    result = mTurk_interface.mTurk.retrieve_recommendation_hit(request.json['username'])
    return jsonify(result), 200


@app.route("/login", methods=['POST'])
def login():
    if not request.json:
        return 'Data is invalid.', 400
    database.database_handler.create_user(request.json['username'])
    return 'OK', 200


@app.route("/get_read_books", methods=['GET'])
def get_read_books():
    if not request.json:
        return 'Data is invalid.', 400
    result = database.database_handler.get_read_books(request.json['username'])
    return jsonify(result), 200


@app.route("/add_read_book", methods=['POST'])
def add_read_book():
    if not request.json:
        return 'Data is invalid.', 400
    result = database.database_handler.add_read_book(request.json['username'], request.json['bookname'],
                                                     request.json['genre'], request.json['rating'])
    return jsonify(result), 200


def retrieve_open_hits():
    print("Sending open hit requests..")
    mTurk_interface.mTurk.generate_verification_tasks()
    mTurk_interface.mTurk.retrieve_verification_tasks()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    database.database_handler.create_db()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=retrieve_open_hits, trigger="interval", seconds=600)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    app.run()

    # mTurk_interface.mTurk.print_account_balance()
    # database.database_handler.create_user("Henk")
    # mTurk_interface.mTurk.create_recommendation("Henk", 'Fantasy', 'Harry Potter and the Order of the Phoenix')
    # mTurk_interface.mTurk.retrieve_recommendation_hit("Henk")
    # mTurk_interface.mTurk.create_verification_task("Henk", "Fantasy", "Harry Potter and the Sorcerer's Ston", ["Test1", "Test2"])
    # mTurk_interface.mTurk.retrieve_verification_tasks()

