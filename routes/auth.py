from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime

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
    
    with open('playergameinfo.json', 'r') as f:
        game_info = json.load(f)
    player_info = None
    for player in game_info:
        if player['user'] == username:
            player_info = player
            break

    return render_template('profile.html', user=user, username=username, player=player_info)

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
        'bio': "None",
        'pfp': "None",
        'role': "user",
        'accountDate': f"{date}"
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