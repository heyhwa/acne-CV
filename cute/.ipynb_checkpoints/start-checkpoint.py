# save this as app.py
from flask import Flask, render_template
import sys

app = Flask(__name__)


@app.route("/") #127.0.0.1
def hello():
    return render_template("hello.html") #127.0.0.1/html/css/b.cs


if __name__ == "__main__":
    app.run(host='0.0.0.0')
    