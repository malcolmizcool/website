from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime, timedelta
import pytz
import json
from models import User
from helpers import data_path

guest = Blueprint('guest', __name__)

@guest.route('/guest')
def guest_page():
    try:
        with open(data_path('guestbook.json'), 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    db_users = User.query.all()
    roles = {u.user: u.role or 'user' for u in db_users}

    online_status = {}
    for user in db_users:
        if not user.lastSeen:
            continue
        last_online = datetime.strptime(user.lastSeen, "%d/%m/%y %H:%M:%S")
        status = datetime.now() - last_online < timedelta(minutes=5)
        online_status[user.user] = status

    current_user = session.get('user')
    return render_template('guestbook/guest.html', entries=entries, users=db_users, roles=roles, online_status=online_status, current_user=current_user)

@guest.route('/sign')
def sign():
    return render_template('guestbook/sign.html')

@guest.route('/deleteGuestEntry', methods=['POST'])
def deleteGuestEntry():
    entry = request.form['index']
    try:
        with open(data_path('guestbook.json'), 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        return f"no guestbook. <a href={"/"}><button>Return Home</button></a>"
    del entries[int(entry)]
    with open(data_path('guestbook.json'), 'w') as f:
        json.dump(entries, f)
    return redirect('/guest')

@guest.route('/process', methods=['POST'])
def process():
    name = session.get('user')
    comment = request.form['message']
    try:
        with open(data_path('guestbook.json'), 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    tz = pytz.timezone('Australia/Melbourne')
    entry = {
        'name': name,
        'message': comment,
        'date': datetime.now(tz).strftime('%d/%m/%y %H:%M')
    }
    if not name or not comment:
        return redirect('/sign')
    entries.insert(0, entry)
    with open(data_path('guestbook.json'), 'w') as f:
        json.dump(entries, f)

    return redirect('/guest')