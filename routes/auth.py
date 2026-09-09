from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime, timedelta
import pytz
import os
import uuid
from werkzeug.utils import secure_filename
from helpers import load_json, get_achievements, award_achievement, get_flairs, calculate_level, xp_needed, data_path
from models import User
from extensions import db

background_images = ['background1.png', 'background2.png']

auth = Blueprint('auth', __name__)

@auth.route('/register')
def register():
    return render_template('auth/register.html')
@auth.route('/login')
def login():
    return render_template('auth/login.html')


@auth.route('/bio/<username>')
def bio(username):
    if username != session.get('user'):
        return 'get lost'
    else:
        db_user = User.query.filter_by(user=username).first()
        if db_user is None:
            db_user = User(user=username, number_of_pokes=0)
            db.session.add(db_user)
            db.session.commit()
        background_images = json.loads(db_user.unlocked_backgrounds or '[]')
        print(background_images)
        return render_template('auth/biopage.html', user=db_user, background_images=background_images)

@auth.route('/backgroundimage/<username>', methods=['GET', 'POST'])
def change_background_image(username):
    if request.method == 'GET':
        return "hmm you shouldnt be here..."
    if request.method == 'POST':
        image = request.form['source']

        user = User.query.filter_by(user=username).first()
        if user:
            user.profile_background_image = image
            db.session.commit()
        
        return redirect(f'/profile/{username}')

@auth.route('/bio/<username>/change', methods=['POST'])
def change_bio(username):
    if username != session.get('user'):
        return 'get lost'
    bio = request.form['bio']
    db_user = User.query.filter_by(user=username).first()
    if db_user is None:
        db_user = User(user=username, number_of_pokes=0)
        db.session.add(db_user)
    db_user.bio = bio
    db.session.commit()
    return redirect(f'/profile/{username}')


@auth.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(user=username).first()
    if user is None:
        return "user not found", 404
    
    user_achievements = get_achievements(username)['achievements']
    user_flairs = get_flairs(username)['flairs']

    show_flairs = False

    game_info = load_json('playergameinfo.json', [])
    player_info = None
    for player in game_info:
        if player['user'] == username:
            player_info = player
            break
    alist = load_json('achievement_list.json', [])
    
    flist = load_json('flair_list.json', [])


    if session.get('user') and session['user'] != username and username == "picklez_gaming":
        award_achievement(session['user'], 'visit_pickle')
    tz = pytz.timezone('Australia/Sydney')
    now = datetime.now(tz)
    last_seen = tz.localize(datetime.strptime(user.lastSeen, "%d/%m/%y %H:%M:%S")) if user.lastSeen else now
    online = now - last_seen < timedelta(minutes=5)
    achieved_achievements = len(user_achievements)
    total_achievements = len(alist)
    fraction = f"{achieved_achievements}/{total_achievements}"
    percentage = (achieved_achievements/total_achievements)*100 if total_achievements else 0
    percentage = round(percentage, 2)

    info = load_json('spininfo.json', [])
    scores = [0]
    for i in info:
        if i['user'] == username:
            scores = i['scores']
            break
    scores.sort(reverse=True)
    score = scores[0]

    if len(user_flairs) >= 1:
        show_flairs = True


    pokeable = False
    if session.get('user') and session.get('user') != username:
        last_poke = session.get(f'last_poke_{username}')
        if last_poke:
            last_poke_time = datetime.fromisoformat(last_poke)
            tz = pytz.timezone('Australia/Sydney')
            if datetime.now(tz) - last_poke_time >= timedelta(days=1):
                pokeable = True
        else:
            pokeable = True

    total_pokes = user.number_of_pokes
    xp = user.xp
    user_level, level_xp, user_xp_needed = calculate_level(xp)
    image = user.profile_background_image



    return render_template('auth/newprofile.html', user=user, username=username, player=player_info, achievements=user_achievements, achievement_list=alist, online=online, last_seen=last_seen, fraction=fraction, percentage=percentage, score=score, flair_list=flist, flairs=user_flairs, show_flairs=show_flairs,
                           pokeable=pokeable,
                           total_pokes=total_pokes, image=image,
                            user_level=user_level, level_xp=level_xp, user_xp_needed=user_xp_needed)

@auth.route('/createAccount', methods=['POST'])
def createAccount():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return f"error <br> <a href={"/"}>Go Home</a>"

    existing = User.query.filter_by(user=username).first()
    if existing is not None and existing.password is not None:
        return f"error <br> <a href={"/"}><button style={"cursor: pointer"}>Go Home</button></a>"

    date = datetime.now().strftime('%d/%m/%y')

    if existing is None:
        new_user = User(user=username, number_of_pokes=0)
        db.session.add(new_user)
    else:
        new_user = existing

    new_user.password = generate_password_hash(password)
    new_user.bio = ""
    new_user.pfp = "None"
    new_user.role = "user"
    new_user.accountDate = date
    new_user.verified = False
    new_user.lastSeen = datetime.now().strftime('%d/%m/%y %H:%M:%S')
    new_user.xp = 0

    session['user'] = username
    session['role'] = new_user.role

    notifications = load_json('notifications.json', [])
    
    new_entry = {
        "user": username,
        "notifications": []
    }

    notifications.append(new_entry)

    with open(data_path('notifications.json'), 'w') as f:
        json.dump(notifications, f)

    db.session.commit()

    return redirect('/')

@auth.route('/loginAccount', methods=['POST'])
def loginAccount():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(user=username).first()
    if user and user.password and check_password_hash(user.password, password):
        session['user'] = username
        session['role'] = user.role
        return redirect('/')

    return f"error <br> <a href={"/"}>Go Home</a>"
    
@auth.route('/logout')
def logout():
    session.clear()
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

@auth.route('/profile/<username>/poke', methods=['GET', 'POST'])
def poke(username):
    if request.method == 'GET':
        return("stop trying to cheat the system 🙄")
    if request.method == 'POST':
        poker = request.form['user']
        notifications = load_json('notifications.json', [])

        for entry in notifications:
            if entry['user'] == username:
                user_notifications = entry['notifications'] 

        tz = pytz.timezone('Australia/Sydney')
        time = datetime.now(tz).isoformat()
        new_notification = {
            "id": str(uuid.uuid4()),
            "title": "New poke!",
            "message": f"{poker} just poked you! You should poke them back.",
            "time": time,
            "is_read": False,
            "type": None
        }
        user_notifications.append(new_notification)
        with open(data_path('notifications.json'), 'w') as f:
            json.dump(notifications, f)
        
        session[f'last_poke_{username}'] = datetime.now(pytz.timezone('Australia/Sydney')).isoformat()

        poked_user = User.query.filter_by(user=username).first()
        if poked_user:
            poked_user.number_of_pokes += 1
            db.session.commit()



        return redirect(f'/profile/{username}')

@auth.route('/notifications')
def show_notifications():
    notifications = load_json('notifications.json', [])
    
    user = session.get('user')
    user_entry = []
    for entry in notifications:
        if entry['user'] == user:
            user_entry = entry
    return render_template('auth/notifications.html', entry=user_entry)

@auth.route('/notifications/delete', methods=['POST'])
def delete_notification():
    notification_id = request.form['notification_id']

    try:
        with open(data_path('notifications.json'), 'r') as f:
            notifications = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        notifications = []

    for entry in notifications:
        entry['notifications'] = [
            n for n in entry['notifications'] if n['id'] != notification_id
        ]

    with open(data_path('notifications.json'), 'w') as f:
        json.dump(notifications, f)

    return redirect('/notifications')
