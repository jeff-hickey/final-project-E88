from flask import render_template
from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template('index.html')


@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)
