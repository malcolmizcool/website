from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from helpers import get_achievements, award_achievement, get_flairs

auth = Blueprint('auth', __name__)

@auth.route('/register')
def register():
    return render_template('register.html')
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/bio/<username>')
def bio(username):
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    user = next((u for u in users if u['username'] == username), None)
    if username != session.get('user'):
        return 'get lost'
    else:
        return render_template('biopage.html', user=user)

@auth.route('/bio/<username>/change', methods=['POST'])
def change_bio(username):
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    if username != session.get('user'):
        return 'get lost'
    bio = request.form['bio']
    for u in users:
        if u['username'] == username:
            u['bio'] = bio
            break
    with open('uandp.json', 'w') as f:
        json.dump(users, f)
    return redirect(f'/profile/{username}')


@auth.route('/profile/<username>')
def profile(username):
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    user = next((u for u in users if u['username'] == username), None)
    if user is None:
        return "user not found", 404
    
    user_achievements = get_achievements(username)['achievements']
    user_flairs = get_flairs(username)['flairs']

    show_flairs = False

    with open('playergameinfo.json', 'r') as f:
        game_info = json.load(f)
    player_info = None
    for player in game_info:
        if player['user'] == username:
            player_info = player
            break
    with open('achievement_list.json', 'r') as f:
        alist = json.load(f)
    
    with open('flair_list.json', 'r') as f:
        flist = json.load(f)
    


    if session.get('user') and session['user'] != username and username == "picklez_gaming":
        award_achievement(session['user'], 'visit_pickle')
    last_seen = datetime.strptime(user['lastSeen'], '%d/%m/%y %H:%M:%S')
    online = datetime.now() - last_seen < timedelta(minutes=5)
    achieved_achievements = len(user_achievements)
    total_achievements = len(alist)
    fraction = f"{achieved_achievements}/{total_achievements}"
    percentage = (achieved_achievements/total_achievements)*100
    percentage = round(percentage, 2)

    with open('spininfo.json', 'r') as f:
        info = json.load(f)
    scores = [0]
    for i in info:
        if i['user'] == username:
            scores = i['scores']
            break
    scores.sort(reverse=True)
    score = scores[0]

    if len(user_flairs) >= 1:
        show_flairs = True

    print('user flairs:')
    print(user_flairs)
    print('flair list')
    print(flist)

    return render_template('profile.html', user=user, username=username, player=player_info, achievements=user_achievements, achievement_list=alist, online=online, last_seen=last_seen, fraction=fraction, percentage=percentage, score=score, flair_list=flist, flairs=user_flairs, show_flairs=show_flairs)

@auth.route('/createAccount', methods=['POST'])
def createAccount():
    username = request.form['username']
    password = request.form['password']
    try:
        with open('uandp.json', 'r') as f:
            details = json.load(f)
            for detail in details:
                if username == detail['username']:
                    return f"error <br> <a href={"/"}><button style={"cursor: pointer"}>Go Home</button></a>"
    except FileNotFoundError:
        details = []
    date = datetime.now().strftime('%d/%m/%y')
    detail = {
        'username': username,
        'password': generate_password_hash(password),
        'bio': "",
        'pfp': "None",
        'role': "user",
        'accountDate': f"{date}",
        'verified': "False",
        'lastSeen': datetime.now().strftime('%d/%m/%y %H:%M:%S'),
        'xp': 0
    }

    if not username or not password:
        return f"error <br> <a href={"/"}>Go Home</a>"
    details.append(detail)
    with open('uandp.json', 'w') as f:
        json.dump(details, f)
    session['user'] = username
    session['role'] = detail['role']
    return redirect('/')

@auth.route('/loginAccount', methods=['POST'])
def loginAccount():
    username = request.form['username']
    password = request.form['password']
    try:
        with open('uandp.json', 'r') as f:
            details = json.load(f)
            for detail in details:
                if username == detail['username'] and check_password_hash(detail['password'], password):
                    session['user'] = username
                    session['role'] = detail['role']
                    print(detail)
                    return redirect('/')
            return f"error <br> <a href={"/"}>Go Home</a>"
    except FileNotFoundError:
        return f"error <br> <a href={"/"}>Go Home</a>"
    
@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@auth.route('/profile/<username>/uploadpfp', methods=['POST'])
def uploadpfp(username):
    if session.get('user') != username:
        return 'get lost'
    
    file = request.files['pfp']
    
    if file.filename == '':
        return redirect(f'/profile/{username}')
    
    if file:
        filename = f"{username}.png"
        file.save(os.path.join('static/avatars', filename))
    
    return redirect(f'/profile/{username}')

@auth.route('/notifications')
def show_notifications():
    with open('notifications.json', 'r') as f:
        notifications = json.load(f)
    
    user = session.get('user')
    user_entry = []
    for entry in notifications:
        if entry['user'] == user:
            user_entry = entry
    return render_template('notifications.html', entry=user_entry)

@auth.route('/notifications/delete', methods=['POST'])
def delete_notification():
    notification_id = request.form['notification_id']

    try:
        with open('notifications.json', 'r') as f:
            notifications = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        notifications = []

    for entry in notifications:
        entry['notifications'] = [
            n for n in entry['notifications'] if n['id'] != notification_id
        ]

    with open('notifications.json', 'w') as f:
        json.dump(notifications, f)

    return redirect('/notifications')