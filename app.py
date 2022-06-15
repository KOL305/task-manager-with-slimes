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
        
        if 'logged_in' in session and session["logged_in"]:
            user = db.users.find_one({'_id': ObjectId(session["logged_in_id"])})
            bal = user['balance']
            return render_template('home.html', bal=bal)
        return render_template('home.html')
    elif request.method == 'POST':
        return render_template('home.html')

@app.route('/tasks', methods=['GET','POST'])
@login_required
def tasks(uid):
    today = datetime.date.today()

    todaySplit = today.strftime("%Y-%m-%d-%H-%M").split("-")
    today = datetime.datetime.strptime(todaySplit[0]+"-"+todaySplit[1]+"-"+todaySplit[2]+"-"+todaySplit[3]+"-"+todaySplit[4], '%Y-%m-%d-%H-%M')
    if request.method == 'GET':
        user = db.users.find_one({'_id': ObjectId(session["logged_in_id"])})
        bal = user['balance']
        tasks = db.tasks.find({'u_id': session['logged_in_id'], 'complete': False}).sort([('duetime', pymongo.ASCENDING)])
        for task in tasks:
            if task['duetime'] < today: #Past due date
                if not(task['late']):
                    db.tasks.update_one({'_id': task['_id']},{
                    '$set': {"reward": task['reward']/2}})
                    db.tasks.update_one({'_id': task['_id']},{
                    '$set': {"late": True}})
        tasksList = list(db.tasks.find({'u_id': session['logged_in_id'], 'complete': False}).sort([('duetime', pymongo.ASCENDING)]))
        for task in tasksList:
            print("obj",str(task['_id']))
            task['_id'] = str(task['_id'])
        print (tasksList)
        return render_template('tasks.html', tasks=tasksList, today=todaySplit, bal=bal)

    return render_template('home.html')

@app.route('/addtask', methods=['POST'])
@login_required
def addtask(uid):
    if request.method == 'POST':
        title=request.get_json()['title']
        duetime=request.get_json()['duetime']
        difficulty=request.get_json()['difficulty']
        notes=request.get_json()['notes']
        reward=(int(difficulty)+1)*2

        duetimeSplit = duetime.split("T")
        duetimeDate = duetimeSplit[0]
        duetimeTime = (duetimeSplit[1]).split(":")
        taskDue = datetime.datetime.strptime(duetimeDate+"-"+duetimeTime[0]+"-"+duetimeTime[1], '%Y-%m-%d-%H-%M') #Saving task due time as yr-mon-day-hr-min

        task = {
            'u_id': session['logged_in_id'],
            'title': title,
            'duetime': taskDue,
            'difficulty': difficulty,
            'notes': notes,
            'reward': reward,
            'late': False,
            'complete': False,
        }

        tasks = db.tasks
        tasks.insert_one(task)

        flash('Task Created', category='success')
        return jsonify({'redirect': '/tasks'})
    return redirect('/home')

@app.route('/deletetask', methods=['POST'])
@login_required
def deletetask(uid):
    if request.method == 'POST':
        taskId = request.get_json()['taskID']
        tasks = db.tasks
        task = tasks.find_one({'_id': ObjectId(taskId)})

        if task:
            tasks.delete_one(task)
            return jsonify({'error': 0})

        return jsonify({'error': 1})

@app.route('/completetask', methods=['POST'])
@login_required
def completetask(uid):
    if request.method == 'POST':
        taskId = request.get_json()['taskID']
        task = db.tasks.find_one({'_id': ObjectId(taskId)})

        if task:
            user = db.users.find_one({'_id': ObjectId(session['logged_in_id'])})
            if user:
                db.tasks.update_one(task, {'$set': {'complete': True}})
                db.users.update_one(user, {'$set': {'balance': user['balance']+task['reward']}})
                return jsonify({'error': 0})
            return jsonify({'error': 1})
        return jsonify({'error': 1})


@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard(uid):
    if request.method == 'GET':
        user = db.users.find_one({'_id': ObjectId(session["logged_in_id"])})
        bal = user['balance']
        return render_template('dashboard.html', bal=bal)

@app.route('/login', methods=['POST'])
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
            
        
@app.route('/signup', methods=['POST'])
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
@login_required
def logout(uid):
    session['logged_in'] = False
    session['logged_in_id'] = ''
    return redirect('/')

if __name__ == "__main__":
    app.config['SECRET_KEY'] = '123qwi34iWge9era89F1393h3gwJ0q3'
    app.run(debug=True)