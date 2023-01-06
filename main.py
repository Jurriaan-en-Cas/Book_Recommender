from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def hello():
    return "Welcome to the Book Recommender Python API"



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run()

