import os
from flask import Flask, render_template, request, redirect, session

import json
from datetime import datetime
import pytz

from routes.auth import auth
from routes.blog import blog
from routes.guest import guest
from routes.jack import jack
from routes.admin import admin

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')


app.register_blueprint(auth)
app.register_blueprint(blog)
app.register_blueprint(guest)
app.register_blueprint(jack)
app.register_blueprint(admin)

pages = ["empty", 
         "faqs", 
         "report",
         "status",
         "thanks",
         "newpost"]

@app.route('/<page>')
def catch(page):
    if page in pages:
        return render_template(page + '.html')
    return "404 not found", 404

@app.before_request
def update_last_seen():
    if request.path.startswith('/static'):
        return  
    if session.get('user'):
        with open('uandp.json', 'r') as f:
            users = json.load(f)
        for user in users:
            if user['username'] == session['user']:
                user['lastSeen'] = datetime.now().strftime('%d/%m/%y %H:%M:%S')
                break
        with open('uandp.json', 'w') as f:
            json.dump(users, f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/games')
def games():
    try:
        with open('playergameinfo.json', 'r') as f:
            playerinfo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        playerinfo = []

    if session.get('user'):
        if not any(p['user'] == session['user'] for p in playerinfo):
            player = {
                'user': session['user'],
                'brating': 1000,
                'bswins': 0,
                'bmwins': 0,
                'tblackjacks': 0
            }
            playerinfo.append(player)
            with open('playergameinfo.json', 'w') as f:
                json.dump(playerinfo, f)

    return render_template('games.html')


@app.route('/reportSubmit', methods=['POST'])
def reportSubmit():

    name = request.form['name']
    feedback = request.form['message']
    try:
        with open('feedback.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    tz = pytz.timezone('Australia/Melbourne')
    entry = {
        'name': name,
        'feedback': feedback,
        'date': datetime.now(tz).strftime('%d/%m/%y %H:%M')
    }
    if not name or not feedback:
        return redirect('/reportSubmit')
    entries.append(entry)
    with open('feedback.json', 'w') as f:
        json.dump(entries, f)
    return render_template('thanks.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)