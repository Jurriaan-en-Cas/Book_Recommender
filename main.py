from flask import Flask, request

import database.database_handler
import mTurk_interface.mTurk

app = Flask(__name__)


@app.route("/")
def hello():
    return "Welcome to the Book Recommender Python API"


@app.route("/recommend", methods = ['POST'])
def recommend():
    if request.form:
        print(request.form["genre"])
        print(request.form["lastread"])
        return 'OK', 200
    else:
        return 'Data is invalid.', 400


@app.route("/login", methods = ['GET'])
def login():
    pass


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # app.run()
    # mTurk_interface.mTurk.print_account_balance()
    database.database_handler.create_db()
    # database.database_handler.create_user("Henk")
    # mTurk_interface.mTurk.create_recommendation("Henk", 'Fantasy', 'Harry Potter and the Order of the Phoenix')
    mTurk_interface.mTurk.retrieve_recommendation_hit("Henk")

