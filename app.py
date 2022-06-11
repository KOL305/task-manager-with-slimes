from functools import wraps
from bson.objectid import ObjectId
import datetime
from flask import Flask, render_template, jsonify, request, redirect, session, abort, flash
from flask_minify import minify
from flask_pymongo import PyMongo
from flask_session import Session
from passlib.hash import pbkdf2_sha256
import pymongo

app = Flask("Task Manager With Slimes")
app.config['MONGO_URI'] = "mongodb://localhost:27017/Task-Manager-With-Slimes-DB"
mongo = PyMongo(app)
app.config['SECRET_KEY'] = '123qwi34iWge9era89F1393h3gwJ0q3'
Session(app)

def login_required(something):
    @wraps(something)
    def wrap_login(*args, **kwargs):
        if 'logged_in' in session and session["logged_in"]:
            return something(session['logged_in_id'], *args, **kwargs)
        else:
            flash("Please Sign In First", category="danger")
            return redirect('/')
    return wrap_login

@app.route('/', methods=['GET','POST'])
def home():
    if request.method == 'GET':
        return render_template('home.html')
    elif request.method == 'POST':
        return render_template('home.html') #need to replace w/ login/register functionality

@app.route('/tasks', methods=['GET','POST'])
def tasks():
    if request.method == 'GET':
        return render_template('tasks.html')

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)