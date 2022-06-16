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

def find_days_month(month, year):
    if month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
        return 31
    elif month == 4 or month == 6 or month == 9 or month == 11:
        return 30
    else:
        if (year%4 == 0 and year%100 != 0) or (year%400 == 0): #If year is leapyear
            return 29
        else:
            return 28

def check_task_status(status, late, onTime):
    if status:
        return late+1, onTime
    else:
        return late, onTime+1

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

@app.route('/shop', methods=['GET', 'POST'])
@login_required
def shop(uid):
    if request.method == 'GET':
        return render_template('shop.html')
    elif request.method == 'POST':
        pass

@app.route('/tasks', methods=['GET','POST'])
@login_required
def tasks(uid):
    today = datetime.datetime.now()
    today = today.strftime('%Y-%m-%d %H:%M:%S')
    today = datetime.datetime.strptime(today, '%Y-%m-%d %H:%M:%S')
    todaySplit = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M').split('-')
    if request.method == 'GET':
        user = db.users.find_one({'_id': ObjectId(session["logged_in_id"])})
        bal = user['balance']
        tasks = db.tasks.find({'u_id': session['logged_in_id'], 'complete': False}).sort([('duetime', pymongo.ASCENDING)])
        for task in tasks:
            print("taskDUe", task['duetime'], "today:", today)
            if task['duetime'] < today: #Past due date
                print("late!")
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
        today=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        print("Today is the", today)

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
            'completeDate': today
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
        today=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        print("This is today",today)
        taskId = request.get_json()['taskID']
        task = db.tasks.find_one({'_id': ObjectId(taskId)})

        if task:
            user = db.users.find_one({'_id': ObjectId(session['logged_in_id'])})
            if user:
                bal = user['balance']+task['reward']
                db.tasks.update_one({'_id': ObjectId(taskId)}, {'$set': {'complete': True}})
                db.tasks.update_one({'_id': ObjectId(taskId)}, {'$set': {'completeDate': today}})
                db.users.update_one(user, {'$set': {'balance': bal}})
                return jsonify({'error': 0, 'redirect': '/tasks'})
            return jsonify({'error': 1})
        return jsonify({'error': 1})


@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard(uid):
    users = db.users
    user = users.find_one({'_id': ObjectId(session['logged_in_id'])})
    if request.method == 'GET':
        user['_id'] = str(user['_id'])
        tasks = list(db.tasks.find({'u_id': session['logged_in_id'], 'complete': True}).sort([('completeDate', pymongo.ASCENDING)]))
        print(tasks)
        today = datetime.date.today().strftime("%Y-%m-%d-%H-%M").split("-")
        thisYear=int(today[0])
        thisMonth=int(today[1])
        thisDay=int(today[2])
        lastYear=thisYear-1
        if thisMonth-1 == 0:
            lastMonth = 12
            lastMonthDays = find_days_month(lastMonth,lastYear)
        else:
            lastMonth = thisMonth-1
            lastMonthDays = find_days_month(lastMonth,thisYear)
        thisMonthDays = find_days_month(thisMonth,thisYear)
        
        aCompletedTasks = len(tasks) #All Time Stats
        aLateTasks = 0
        aOnTimeTasks = 0
        aCoinsEarned = 0
        if tasks:
            firstTaskDate = tasks[0]["completeDate"].split("-")
        else:
            firstTaskDate = [today[0],today[1],today[2]]
        
        yCompletedTasks = 0 #Yearly Stats
        yLateTasks = 0
        yOnTimeTasks = 0
        yCoinsEarned = 0
        
        mCompletedTasks = 0 #Monthly Stats
        mLateTasks = 0
        mOnTimeTasks = 0
        mCoinsEarned = 0

        lyCompletedTasks = 0 #Last Yearly Stats
        lyLateTasks = 0
        lyOnTimeTasks = 0
        lyCoinsEarned = 0

        lmCompletedTasks = 0 #Last Monthly Stats
        lmLateTasks = 0
        lmOnTimeTasks = 0
        lmCoinsEarned = 0
        
        allTimeFrame = {}
        cAllTimeFrame = {}
        thisYearFrame = {}
        cThisYearFrame = {}
        lastYearFrame = {}
        cLastYearFrame = {}
        thisMonthFrame = {}
        cThisMonthFrame = {}
        lastMonthFrame = {}
        cLastMonthFrame = {}

        increments = ((int(today[0])-int(firstTaskDate[0]))+1)*12
        iYearAdd = 0
        for i in range (increments):
            if i%12 == 0 and i!=0:
                iYearAdd+=1
            allTimeFrame[str(int(firstTaskDate[0])+iYearAdd)[2:4]+"-"+str(i%12+1).zfill(2)] = 0
            cAllTimeFrame[str(int(firstTaskDate[0])+iYearAdd)[2:4]+"-"+str(i%12+1).zfill(2)] = 0

        for i in range(1,13):
            thisYearFrame[str(thisYear)[2:4]+"-"+str(i).zfill(2)] = 0
            cThisYearFrame[str(thisYear)[2:4]+"-"+str(i).zfill(2)] = 0 #Can just do uThisYearFrame = thisYearFrame?
            lastYearFrame[str(thisYear)[2:4]+"-"+str(i).zfill(2)] = 0
            cLastYearFrame[str(thisYear)[2:4]+"-"+str(i).zfill(2)] = 0

        for day in range(thisMonthDays):
            thisMonthFrame[day+1] = 0
            cThisMonthFrame[day+1] = 0

        for day in range(lastMonthDays):
            lastMonthFrame[day+1] = 0
            cLastMonthFrame[day+1] = 0

        for task in tasks:
            task_coins = task['reward']
            task_status = task['late']
            date_time_obj_list = task['completeDate'].split("-")
            task_year = int(date_time_obj_list[0])
            task_month = int(date_time_obj_list[1])
            task_day = int(date_time_obj_list[2])

            allTimeFrame[str(int(firstTaskDate[0])+iYearAdd)[2:4]+"-"+str(task_month).zfill(2)]+=1
            cAllTimeFrame[str(int(firstTaskDate[0])+iYearAdd)[2:4]+"-"+str(task_month).zfill(2)]+=task_coins

            aCoinsEarned+=task_coins

            if task_year==thisYear: #Finding if task in current year
                yCompletedTasks+=1
                yCoinsEarned+=task_coins
                thisYearFrame[str(thisYear)[2:4]+"-"+str(task_month).zfill(2)]+=1
                cThisYearFrame[str(thisYear)[2:4]+"-"+str(task_month).zfill(2)]+=task_coins
                if task_month==thisMonth: #Finding if task in current month
                    mCompletedTasks+=1
                    mCoinsEarned+=task_coins
                    thisMonthFrame[task_day]+=1
                    cThisMonthFrame[task_day]+=task_coins
                    mLateTasks, mOnTimeTasks = check_task_status(task_status, mLateTasks, mOnTimeTasks)
                elif task_month==lastMonth: #Finding if task in last month
                    lmCompletedTasks+=1
                    lmCoinsEarned+=task_coins
                    lastMonthFrame[task_day]+=1
                    cLastMonthFrame[task_day]+=task_coins
                    lmLateTasks, lmOnTimeTasks = check_task_status(task_status, lmLateTasks, lmOnTimeTasks)
                yLateTasks, yOnTimeTasks = check_task_status(task_status, yLateTasks, yOnTimeTasks)
            elif task_year==lastYear: #Finding if task in last year
                lyCompletedTasks+=1
                lyCoinsEarned+=task_coins
                lastYearFrame[str(lastYear)[2:4]+"-"+str(task_month).zfill(2)]+=1
                cLastYearFrame[str(lastYear)[2:4]+"-"+str(task_month).zfill(2)]+=task_coins
                lyLateTasks, lmOnTimeTasks = check_task_status(task_status, lyLateTasks, lyOnTimeTasks)
                if task_month==lastMonth: #Finding if task in last month
                    lmCompletedTasks+=1
                    lmCoinsEarned+=task_coins
                    lastMonthFrame[task_day]+=1
                    cLastMonthFrame[task_day]+=task_coins
                    lmLateTasks, lmOnTimeTasks = check_task_status(task_status, lmLateTasks, lmOnTimeTasks)
            aLateTasks, aOnTimeTasks = check_task_status(task_status, aLateTasks, aOnTimeTasks)

        allTimeStats = {'dataset': allTimeFrame, 'cDataset': cAllTimeFrame,'completedTasks': aCompletedTasks, 'lateTasks': aLateTasks, 'onTimeTasks': aOnTimeTasks, 'coins': aCoinsEarned, 'firstTaskDate': firstTaskDate}
        thisYearStats = {'dataset': thisYearFrame, 'cDataset': cThisYearFrame, 'completedTasks': yCompletedTasks, 'lateTasks': yLateTasks, 'onTimeTasks': yOnTimeTasks, 'coins': yCoinsEarned}
        lastYearStats = {'dataset': lastYearFrame, 'cDataset': cLastYearFrame, 'completedTasks': lyCompletedTasks, 'lateTasks': lyLateTasks, 'onTimeTasks': lyOnTimeTasks, 'coins': lyCoinsEarned}
        thisMonthStats = {'dataset': thisMonthFrame, 'cDataset': cThisMonthFrame, 'completedTasks': mCompletedTasks, 'lateTasks': mLateTasks, 'onTimeTasks': mOnTimeTasks, 'coins': mCoinsEarned}
        lastMonthStats = {'dataset': lastMonthFrame, 'cDataset': cLastMonthFrame, 'completedTasks': lmCompletedTasks, 'lateTasks': lmLateTasks, 'onTimeTasks': lmOnTimeTasks, 'coins': lmCoinsEarned}

        return render_template('dashboard.html', user=user, bal=user['balance'], allTimeStats=allTimeStats, thisYearStats=thisYearStats, lastYearStats=lastYearStats, thisMonthStats=thisMonthStats, lastMonthStats=lastMonthStats)
    elif request.method == "POST":
        requestType = request.get_json()['requestType']
        if requestType == "changePassword":
            oldPassword = request.get_json()['oldPass']
            newPassword = request.get_json()['newPass']
            if pbkdf2_sha256.verify(oldPassword, user['password_hash']):
                users.update_one({'_id': ObjectId(session['logged_in_id'])}, {
                    '$set': {'password_hash': pbkdf2_sha256.hash(newPassword)}})
                return jsonify({"error": "0", "message": "Password Successfully Changed"})
            else:
                return jsonify({"error": "1", "message": "Current Password Does Not Match With Database", "type": "oldPass"})

        elif requestType == "changeUsername":
            username = request.get_json()['username']
            if users.find_one({"username": username}) is not None:
                return jsonify({"error": "1", "message": "Username Already Exists"})
            else:
                users.update_one({'_id': ObjectId(session['logged_in_id'])}, {
                    '$set': {'username': username}})
                return jsonify({"error": "0", "message": "Username Successfully Changed"})

        elif requestType == "deleteAccount":
            users.delete_one(user)
            flash("Account Successfully Deleted", category="success")
            return jsonify({"error": "0", "message": "Account Successfully Deleted"})

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

                newShopUser = {
                    "u_id": session['logged_in_id'],
                    "slimeColor": "Unselected",
                    "slimeTop": "Unselected",
                    "slimeColorOwned": [],
                    "slimeTopOwned": []
                }
                db.shop.insert_one(newShopUser)

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