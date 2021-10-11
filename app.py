from flask import Flask, render_template, request, redirect, url_for

from utils.maps import create_map, create_new_place


app = Flask(__name__)


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/oops')
def oops():
    return render_template('oops.html')


@app.get('/ping')
def update_map():
    created = create_map()
    if created:
        return render_template('index.html')
    return redirect(url_for('oops'))


@app.post('/places')
def new_place():
    place_data = request.json
    create_new_place(place_data)
    created = create_map()
    if created:
        return render_template('index.html')
    return redirect(url_for('oops'))
