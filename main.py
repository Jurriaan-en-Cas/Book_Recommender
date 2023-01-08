from flask import Flask, request

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
    app.run()

