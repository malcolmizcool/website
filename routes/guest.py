from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime, timedelta
import pytz
import json

guest = Blueprint('guest', __name__)

@guest.route('/guest')
def guest_page():
    try:
        with open('guestbook.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    with open('uandp.json', 'r') as f:
        users  = json.load(f)
    roles = {u['username']: u.get('role', 'user') for u in users}

    online_status = {}
    for user in users:
        last_online = datetime.strptime(user['lastSeen'], "%d/%m/%y %H:%M:%S")
        status = datetime.now() - last_online < timedelta(minutes=5)
        online_status[user['username']] = status

    current_user = session.get('user')
    return render_template('guest.html', entries=entries, users=users, roles=roles, online_status=online_status, current_user=current_user)

@guest.route('/sign')
def sign():
    return render_template('sign.html')

@guest.route('/deleteGuestEntry', methods=['POST'])
def deleteGuestEntry():
    entry = request.form['index']
    try:
        with open('guestbook.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        return f"no guestbook. <a href={"/"}><button>Return Home</button></a>"
    del entries[int(entry)]
    with open('guestbook.json', 'w') as f:
        json.dump(entries, f)
    return redirect('/guest')

@guest.route('/process', methods=['POST'])
def process():
    name = session.get('user')
    comment = request.form['message']
    try:
        with open('guestbook.json', 'r') as f:
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
    with open('guestbook.json', 'w') as f:
        json.dump(entries, f)

    return redirect('/guest')