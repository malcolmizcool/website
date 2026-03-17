from flask import Blueprint, render_template, request, redirect, session
import json
from datetime import datetime
import os
from helpers import award_achievement

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

@admin.route('/admin/achievement/add', methods=['POST'])
def add_achievement():
    id = request.form['achievementid']
    name = request.form['achievementname']
    description = request.form['achievementdescription']
    colour = request.form['achievementcolour']
    new_achievement = {
        "id": id,
        "name": name,
        "description": description,
        "rarity": colour
    }
    try:
        with open('achievement_list.json', 'r') as f:
            achievements = json.load(f)
    except:
        achievements = []
    achievements.append(new_achievement)
    with open('achievement_list.json', 'w') as f:
        json.dump(achievements, f)
    return redirect('/admin')
    
@admin.route('/admin/achievement/award', methods=['POST'])
def award_player_achievement():
    user = request.form['user']
    achievement_id = request.form['achievementid']
    award_achievement(user, achievement_id)
    return redirect('/admin')



@admin.route('/admin')
def admin_page():
    return render_template('admin.html')