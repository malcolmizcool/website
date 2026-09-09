from flask import Blueprint, render_template, request, redirect, session, flash
import json
from datetime import datetime
import os
from helpers import load_json, award_achievement, award_flair, require_admin, data_path
import uuid
import pytz
from models import User
from extensions import db

admin = Blueprint('admin', __name__)



@admin.route('/admin')
@require_admin
def admin_page():
    show_achievements = request.args.get('show') == 'achievements'
    show_flairs = request.args.get('show') == 'flairs'

    
    try:
        with open(data_path('flair_list.json'), 'r') as f:
            flair_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        flair_list = []

    users = User.query.all()

    try:
        with open(data_path('ranks.json'), 'r') as f:
            ranks = json.load(f)
    except:
        ranks = ["error: im sorry but i cant read the ranks file at the moment", "user", "admin"]


    try:
        with open(data_path('achievement_list.json'), 'r') as f:
            achievement_list = json.load(f)
    except:
        achievement_list = [{"id": "error", "name": "Error", "description": "I'm sorry, but I can't read the achievement list at the moment.", "rarity": "error"}]

    return render_template('admin/admin.html', achievement_list=achievement_list, show_achievements=show_achievements, flair_list = flair_list, show_flairs=show_flairs,
                           users=users, ranks=ranks)

@admin.route('/admin/migrategame')
@require_admin
def migrate_game():
    return render_template('admin/migrategameinfo.html')

@admin.route('/admin/migratenumber', methods=['POST'])
@require_admin
def migrate_number():
    newfield = request.form['newfield']
    default_value = request.form['value']
    try:
        with open(data_path('spininfo.json'), 'r') as f:
            players = json.load(f)
    except:
        players = []
    for player in players:
        if newfield not in player:
            player[newfield] = default_value
    
    with open(data_path('spininfo.json'), 'w') as f:
        json.dump(players, f)
    
    return f"done <a href='/admin'>do another</a>"


@admin.route('/admin/updateannouncements', methods=['POST'])
@require_admin
def update_announcements():
    new_announcement = request.form['newannouncement']



    try:
        with open(data_path('announcements.json'), 'r') as f:
            announcements = json.load(f)
    except:
        announcements = []
    announcements.insert(0, new_announcement)

    with open(data_path('announcements.json'), 'w') as f:
        json.dump(announcements, f)

    return redirect("/")

@admin.route('/admin/updatelinks', methods=['POST'])
@require_admin
def update_links():
    new_link = request.form['new_link']
    new_link_text = request.form['new_link_text']
    new_caption = request.form['new_caption']

    try:
        with open(data_path('links.json'), 'r') as f:
            links = json.load(f)
    except:
        links = []

    links.insert(0, {"link": new_link,
                     "link_text": new_link_text,
                     "caption": new_caption})

    with open(data_path('links.json'), 'w') as f:
        json.dump(links, f)

    return redirect("/")


@admin.route('/admin/deleteAnnouncement', methods=['POST'])
@require_admin
def delete_announcement():
    index = request.form['index']

    try:
        with open(data_path('announcements.json'), 'r') as f:
            announcements = json.load(f)
    except:
        return("hmm that didnt work. Maybe the announcement doesn't exist? I cant read the announcement file at all.")

    del announcements[int(index)]

    with open(data_path('announcements.json'), 'w') as f:
        json.dump(announcements, f)

    return redirect('/')

@admin.route('/admin/deleteLink', methods=['POST'])
@require_admin
def delete_link():
    index = request.form['index']

    try:
        with open(data_path('links.json'), 'r') as f:
            links = json.load(f)
    except:
        return("hmm that didnt work. Maybe the link doesn't exist? I cant read the link file at all.")

    del links[int(index)]

    with open(data_path('links.json'), 'w') as f:
        json.dump(links, f)

    return redirect('/')

    

@admin.route('/admin/migrategame', methods=['POST'])
@require_admin
def migrategame():
    newfield = request.form['newfield']
    default_value = request.form['value']
    
    players = load_json('playergameinfo.json', [])
    
    for player in players:
        if newfield not in player:
            player[newfield] = default_value
    
    with open(data_path('playergameinfo.json'), 'w') as f:
        json.dump(players, f)
    
    return f"done <a href='/admin'>do another</a>"

@admin.route('/admin/migrateuandp')
@require_admin
def migrate_uandp():
    if session.get('user') != 'malcolm':
        return "nope"
    return "User accounts now live in the database, not uandp.json, so this bulk field-adder no longer applies. To add a new field to all users, add a column to the User model in models.py and run a database migration instead. <a href='/admin'>Back</a>"

@admin.route('/admin/userrank', methods=['POST'])
@require_admin
def user_rank():
    username = request.form['user']
    rank = request.form['newrank']
    user = User.query.filter_by(user=username).first()
    if user:
        user.role = rank
        db.session.commit()
    return redirect('/admin')

@admin.route('/admin/feedback')
@require_admin
def show_feedback():
    feedback = load_json('feedback.json', [])
    
    return render_template('admin/showfeedback.html', feedback=feedback)

@admin.route('/admin/feedback/delete', methods=['POST'])
@require_admin
def delete_feedback():
    entry = request.form['index']
    try:
        with open(data_path('feedback.json'), 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        return f"no feedback. <a href={"/admin"}><button>Return Home</button></a>"
    del entries[int(entry)]
    with open(data_path('feedback.json'), 'w') as f:
        json.dump(entries, f)
    return redirect('/admin/feedback')

@admin.route('/admin/users')
@require_admin
def show_users():
    users = User.query.all()
    return render_template('admin/adminusers.html', users=users)

@admin.route('/admin/achievement/add', methods=['POST'])
@require_admin
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
        with open(data_path('achievement_list.json'), 'r') as f:
            achievements = json.load(f)
    except:
        achievements = []
    achievements.append(new_achievement)
    with open(data_path('achievement_list.json'), 'w') as f:
        json.dump(achievements, f)
    return redirect('/admin')
    
@admin.route('/admin/achievement/award', methods=['POST'])
@require_admin
def award_player_achievement():
    user = request.form['user']
    achievement_id = request.form['achievementid']
    award_achievement(user, achievement_id)
    return redirect('/admin')

@admin.route('/admin/flair/add', methods=['POST'])
@require_admin
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
        with open(data_path('flair_list.json'), 'r') as f:
            achievements = json.load(f)
    except:
        achievements = []
    achievements.append(new_achievement)
    with open(data_path('flair_list.json'), 'w') as f:
        json.dump(achievements, f)
    return redirect('/admin')
    
@admin.route('/admin/flair/award', methods=['POST'])
@require_admin
def award_player_flair():
    user = request.form['user']
    achievement_id = request.form['achievementid']
    award_flair(user, achievement_id)
    return redirect('/admin')


@admin.route('/admin/achievement/delete', methods=['POST'])
@require_admin
def delete_achievement():
    achievement_id = request.form['id']
    achievements = load_json('achievement_list.json', [])
    achievements = [a for a in achievements if a['id'] != achievement_id]
    with open(data_path('achievement_list.json'), 'w') as f:
        json.dump(achievements, f)
    users = load_json('achievements.json', [])
    for user in users:
        user['achievements'] = [a for a in user['achievements'] if a != achievement_id]
    with open(data_path('achievements.json'), 'w') as f:
        json.dump(users, f)
    return redirect('/admin?show=achievements')

@admin.route('/admin/flair/delete', methods=['POST'])
@require_admin
def delete_flair():
    achievement_id = request.form['id']
    achievements = load_json('flair_list.json', [])
    achievements = [a for a in achievements if a['id'] != achievement_id]
    with open(data_path('flair_list.json'), 'w') as f:
        json.dump(achievements, f)
    users = load_json('flairs.json', [])
    for user in users:
        user['flairs'] = [a for a in user['flairs'] if a != achievement_id]
    with open(data_path('flairs.json'), 'w') as f:
        json.dump(users, f)
    return redirect('/admin?show=flairs')

@admin.route('/admin/notification/direct', methods=['POST'])
@require_admin
def send_direct_notification():
    user = request.form['user']
    title = request.form['title']
    message = request.form['message']
    tz = pytz.timezone('Australia/Sydney')
    time = datetime.now(tz).isoformat()

    notifications = load_json('notifications.json', [])

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

    with open(data_path('notifications.json'), 'w') as f:
        json.dump(notifications, f)

    return redirect('/admin')

@admin.route('/admin/notifications/universal', methods=['POST'])
@require_admin
def send_universal_notification():
    title = request.form['title']
    message = request.form['message']
    tz = pytz.timezone('Australia/Sydney')
    time = datetime.now(tz).isoformat()

    users = User.query.all()

    try:
        with open(data_path('notifications.json'), 'r') as f:
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
        entry = next((e for e in notifications if e['user'] == user.user), None)
        if entry is None:
            entry = {'user': user.user, 'notifications': []}
            notifications.append(entry)
        entry['notifications'].append(new_notification)

    with open(data_path('notifications.json'), 'w') as f:
        json.dump(notifications, f)

    return redirect('/admin')