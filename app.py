from flask import Flask, render_template, request, redirect, url_for
from flask_cors import cross_origin

from utils.decorators import requires_auth
from utils.maps import create_map, create_new_place


app = Flask(__name__)


@app.get('/')
def home():
    return render_template('index.html')


@app.get('/oops')
def oops():
    return render_template('oops.html')


@app.get('/ping')
@cross_origin(allow_headers=["Content-Type", "Authorization"])
@requires_auth
def update_map():
    created = create_map()
    if created:
        return render_template('index.html')
    return redirect(url_for('oops'))


@app.post('/places')
@cross_origin(allow_headers=["Content-Type", "Authorization"])
@requires_auth
def new_place():
    place_data = request.json
    create_new_place(place_data)
    created = create_map()
    if created:
        return render_template('index.html')
    return redirect(url_for('oops'))
