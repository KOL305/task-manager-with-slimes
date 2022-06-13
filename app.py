from functools import wraps
from bson.objectid import ObjectId
import datetime
from flask import Flask, render_template, jsonify, request, redirect, session, abort, flash
from flask_minify import minify
from flask_pymongo import PyMongo
from flask_session import Session
from passlib.hash import pbkdf2_sha256
import pymongo
from config import Config, db

app = Flask("Task Manager With Slimes")
app.config.from_object(Config)
client = PyMongo(app)
db = client.db
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

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        print('ab')
        print(request.data)
        username=request.get_json()['username']
        print(username)
        print('a')
        password=request.get_json()['password']
        print(password)
        print('b')
        users = db.users
        user = users.find_one({
            'username': username,
        })
        if user is not None and pbkdf2_sha256.verify(password, user['password_hash']):
            session['logged_in'] = True
            session['logged_in_id'] = str(user['_id'])
            flash('Successful Login', category='success')
            return jsonify({'redirect': '/dashboard'})
        else:
            if user is None:
                return jsonify({"error": "1", "message": "invalid username"})
            else:
                return jsonify({"error": "2", "message": "incorrect password"})
    return redirect('/')
            
        
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        print(request.json)
        print('data', request.data)
        username=request.get_json()['username']
        password=request.get_json()['password']
        cpassword=request.get_json()['confirm_password']
        users = db.users
        newUser = {
            "username": username,
            "password_hash": pbkdf2_sha256.hash(password),
        }
        if users.find_one({'username': newUser['username']}) is None:
            if password == cpassword:
                users.insert_one(newUser)
                user = users.find_one({'username': username})
                session['logged_in'] = True
                session['logged_in_id'] = str(user['_id'])
                flash('Account Successfully Created', category='success')
                return jsonify({'redirect': '/dashboard'})
            else:
                return jsonify({"error": "2", "message": "passwords do not match"})
        else:
            return jsonify({"error": "1", "message": "username already in use"})
    return redirect('/')

@app.route('/logout', methods=['GET','POST'])
def logout():
    session['logged_in'] = False
    session['logged_in_id'] = ''
    return redirect('/')

if __name__ == "__main__":
    app.config['SECRET_KEY'] = '123qwi34iWge9era89F1393h3gwJ0q3'
    app.run(debug=True)