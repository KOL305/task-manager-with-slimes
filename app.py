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
        return render_template('home.html')

@app.route('/tasks', methods=['GET','POST'])
def tasks():
    today = datetime.date.today()
    todaySplit = today.strftime("%Y-%m-%d-%H-%M").split("-")
    today = datetime.datetime.strptime(todaySplit[0]+"-"+todaySplit[1]+"-"+todaySplit[2]+"-"+todaySplit[3]+"-"+todaySplit[4], '%Y-%m-%d-%H-%M')
    if request.method == 'GET':
        tasks = db.tasks.find({'u_id': session['logged_in_id']}).sort([('duetime', pymongo.ASCENDING)])
        for task in tasks:
            if task['duetime'] < today: #Past due date
                db.tasks.update_one({'_id': task['_id']},{
                '$set': {"late": True}})
        tasks = db.tasks.find({'u_id': session['logged_in_id']}).sort([('duetime', pymongo.ASCENDING)])
        return render_template('tasks.html', tasks=tasks, today=todaySplit)
    elif request.method == "POST":
        title=request.get_json()['title']
        duetime=request.get_json()['duetime']
        difficulty=request.get_json()['difficulty']
        notes=request.get_json()['notes']

        duetimeSplit = duetime.split("T")
        print("dtsplit", duetimeSplit)
        duetimeDate = duetimeSplit[0]
        duetimeTime = (duetimeSplit[1]).split(":")
        print("daaaea",duetimeDate,duetimeTime)
        taskDue = datetime.datetime.strptime(duetimeDate+"-"+duetimeTime[0]+"-"+duetimeTime[1], '%Y-%m-%d-%H-%M') #Saving task due time as yr-mon-day-hr-min
        print("taskdeu", taskDue)

        task = {
            'u_id': session['logged_in_id'],
            'title': title,
            'duetime': taskDue,
            'difficulty': difficulty,
            'notes': notes,
            'late': False,
        }

        tasks = db.tasks
        tasks.insert_one(task)

        flash('Task Created', category='success')
        return jsonify({'redirect': '/tasks'})


@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if request.method == 'GET':
        return render_template('dashboard.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.get_json()['username']
        password=request.get_json()['password']
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
            "balance": 0,
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