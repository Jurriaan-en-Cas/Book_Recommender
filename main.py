from flask import Flask, request, json

import database.database_handler
import mTurk_interface.mTurk

app = Flask(__name__)


@app.route("/")
def hello():
    return "Welcome to the Book Recommender Python API"


@app.route("/recommend", methods=['POST'])
def recommend():
    if request.json:
        print(request.json['username'])
        mTurk_interface.mTurk.create_recommendation(request.json['username'], request.json['genre'], request.json['book'])
        return 'OK', 200
    else:
        return 'Data is invalid.', 400


@app.route("/login", methods=['POST'])
def login():
    if not request.json:
        return 'Data is invalid.', 400
    database.database_handler.create_user(request.json['username'])
    return 'OK', 200


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    database.database_handler.create_db()
    app.run()
    # mTurk_interface.mTurk.print_account_balance()
    # database.database_handler.create_user("Henk")
    # mTurk_interface.mTurk.create_recommendation("Henk", 'Fantasy', 'Harry Potter and the Order of the Phoenix')
    # mTurk_interface.mTurk.retrieve_recommendation_hit("Henk")

