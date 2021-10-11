from flask import Flask, render_template


app = Flask(__name__)


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/oops')
def oops():
    return render_template('oops.html')
