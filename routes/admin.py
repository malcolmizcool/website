from flask import Blueprint, render_template, request, redirect, session
import json
from datetime import datetime
import os

admin = Blueprint('admin', __name__)

@admin.route('/admin/migrategame')
def migrate_game():
    return render_template('migrategameinfo.html')

@admin.route('/admin/migrategame', methods=['POST'])
def migrategame():
    newfield = request.form['newfield']
    default_value = request.form['value']
    
    with open('playergameinfo.json', 'r') as f:
        players = json.load(f)
    
    for player in players:
        if newfield not in player:
            player[newfield] = default_value
    
    with open('playergameinfo.json', 'w') as f:
        json.dump(players, f)
    
    return f"done <a href='/admin'>do another</a>"

@admin.route('/admin/migrateuandp')
def migrate_uandp():
    if session.get('user') != 'malcolm':
        return "nope"
    return render_template('migrateuandp.html')

@admin.route('/admin/migrateuandp', methods=['POST'])
def migrateuandp():
    newfield = request.form['newfield']
    default_value = request.form['value']
    
    with open('uandp.json', 'r') as f:
        players = json.load(f)
    
    for player in players:
        if newfield not in player:
            player[newfield] = default_value
    
    with open('uandp.json', 'w') as f:
        json.dump(players, f)
    
    return f"done <a href='/admin'>do another</a>"

@admin.route('/admin/userrank', methods=['POST'])
def user_rank():
    username = request.form['user']
    rank = request.form['newrank']
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    for user in users:
        if user['username'] == username:
            user['role'] = rank
    with open('uandp.json', 'w') as f:
        json.dump(users, f)
    return redirect('/admin')

@admin.route('/admin/feedback')
def show_feedback():
    with open('feedback.json', 'r') as f:
        feedback = json.load(f)
    
    return render_template('showfeedback.html', feedback=feedback)

@admin.route('/admin/feedback/delete', methods=['POST'])
def delete_feedback():
    entry = request.form['index']
    try:
        with open('feedback.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        return f"no feedback. <a href={"/admin"}><button>Return Home</button></a>"
    del entries[int(entry)]
    with open('feedback.json', 'w') as f:
        json.dump(entries, f)
    return redirect('/admin/feedback')

@admin.route('/admin/users')
def show_users():
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    return render_template('adminusers.html', users=users)



@admin.route('/admin')
def admin_page():
    return render_template('admin.html')