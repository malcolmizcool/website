from flask import Blueprint, render_template, request, redirect, session
import json
from datetime import datetime
import os
from helpers import award_achievement, award_flair
import uuid

admin = Blueprint('admin', __name__)

@admin.route('/admin/migrategame')
def migrate_game():
    return render_template('migrategameinfo.html')

@admin.route('/admin/migratenumber', methods=['POST'])
def migrate_number():
    newfield = request.form['newfield']
    default_value = request.form['value']
    try:
        with open('spininfo.json', 'r') as f:
            players = json.load(f)
    except:
        players = []
    for player in players:
        if newfield not in player:
            player[newfield] = default_value
    
    with open('spininfo.json', 'w') as f:
        json.dump(players, f)
    
    return f"done <a href='/admin'>do another</a>"

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

@admin.route('/admin/flair/add', methods=['POST'])
def add_flair():
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
        with open('flair_list.json', 'r') as f:
            achievements = json.load(f)
    except:
        achievements = []
    achievements.append(new_achievement)
    with open('flair_list.json', 'w') as f:
        json.dump(achievements, f)
    return redirect('/admin')
    
@admin.route('/admin/flair/award', methods=['POST'])
def award_player_flair():
    user = request.form['user']
    achievement_id = request.form['achievementid']
    award_flair(user, achievement_id)
    return redirect('/admin')

@admin.route('/admin')
def admin_page():
    show_achievements = request.args.get('show') == 'achievements'
    show_flairs = request.args.get('show') == 'flairs'
    try:
        with open('achievement_list.json', 'r') as f:
            achievement_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        achievement_list = []
    
    try:
        with open('flair_list.json', 'r') as f:
            flair_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        flair_list = []

    return render_template('admin.html', achievement_list=achievement_list, show_achievements=show_achievements, flair_list = flair_list, show_flairs=show_flairs)

@admin.route('/admin/achievement/delete', methods=['POST'])
def delete_achievement():
    achievement_id = request.form['id']
    with open('achievement_list.json', 'r') as f:
        achievements = json.load(f)
    achievements = [a for a in achievements if a['id'] != achievement_id]
    with open('achievement_list.json', 'w') as f:
        json.dump(achievements, f)
    with open('achievements.json', 'r') as f:
        users = json.load(f)
    for user in users:
        user['achievements'] = [a for a in user['achievements'] if a != achievement_id]
    with open('achievements.json', 'w') as f:
        json.dump(users, f)
    return redirect('/admin?show=achievements')

@admin.route('/admin/flair/delete', methods=['POST'])
def delete_flair():
    achievement_id = request.form['id']
    with open('flair_list.json', 'r') as f:
        achievements = json.load(f)
    achievements = [a for a in achievements if a['id'] != achievement_id]
    with open('flair_list.json', 'w') as f:
        json.dump(achievements, f)
    with open('flairs.json', 'r') as f:
        users = json.load(f)
    for user in users:
        user['flairs'] = [a for a in user['flairs'] if a != achievement_id]
    with open('flairs.json', 'w') as f:
        json.dump(users, f)
    return redirect('/admin?show=flairs')

@admin.route('/admin/notification/direct', methods=['POST'])
def send_direct_notification():
    user = request.form['user']
    title = request.form['title']
    message = request.form['message']
    time = datetime.now().isoformat()

    with open('notifications.json', 'r') as f:
        notifications = json.load(f)

    new_notification = {
        'id': str(uuid.uuid4()),
        'title': title,
        'message': message,
        'time': time,
        'is_read': False,
        'type': None
    }

    user_entry = None
    for entry in notifications:
        if entry['user'] == user:
            user_entry = entry
            break

    if user_entry:
        user_entry['notifications'].append(new_notification)
    else:
        notifications.append({
            'user': user,
            'notifications': [new_notification]
        })

    with open('notifications.json', 'w') as f:
        json.dump(notifications, f)

    return redirect('/admin')

@admin.route('/admin/notifications/universal', methods=['POST'])
def send_universal_notification():
    title = request.form['title']
    message = request.form['message']
    time = datetime.now().isoformat()

    try:
        with open('uandp.json', 'r') as f:
            users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        users = []

    try:
        with open('notifications.json', 'r') as f:
            notifications = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        notifications = []

    new_notification = {
        'id': str(uuid.uuid4()),
        'title': title,
        'message': message,
        'time': time,
        'is_read': False,
        'type': None
    }

    for user in users:
        entry = next((e for e in notifications if e['user'] == user['username']), None)
        if entry is None:
            entry = {'user': user['username'], 'notifications': []}
            notifications.append(entry)
        entry['notifications'].append(new_notification)

    with open('notifications.json', 'w') as f:
        json.dump(notifications, f)

    return redirect('/admin')