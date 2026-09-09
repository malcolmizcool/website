import json
from models import User
from extensions import db
from flask import session, redirect
from functools import wraps



def require_admin(f):
    """Blocks a route unless the logged-in user's role in the database is 'admin'.
    Checks the live database, not the cached session role, so a rank change
    takes effect immediately without needing to log out and back in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user'):
            return redirect('/login')
        current = User.query.filter_by(user=session['user']).first()
        if not current or (current.role or 'user') != 'admin':
            return "not authorised", 403
        return f(*args, **kwargs)
    return decorated


def get_achievements(username):
    try:
        with open('achievements.json', 'r') as f:
            achievements = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        achievements = []
    
    user_achievements = next((a for a in achievements if a['user'] == username), None)
    
    if user_achievements is None:
        user_achievements = {'user': username, 'achievements': []}
        achievements.append(user_achievements)
        with open('achievements.json', 'w') as f:
            json.dump(achievements, f)

    return user_achievements


def get_flairs(username):
    try:
        with open('flairs.json', 'r') as f:
            flairs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        flairs = []
    
    user_flairs = next((a for a in flairs if a['user'] == username), None)
    
    if user_flairs is None:
        user_flairs = {'user': username, 'flairs': []}
        flairs.append(user_flairs)
        with open('flairs.json', 'w') as f:
            json.dump(flairs, f)

    return user_flairs

def award_achievement(user, achievement_id):
    try:
        with open('achievements.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    
    try:
        with open('achievement_list.json', 'r') as f:
            achievements = json.load(f)
    except FileNotFoundError:
        achievements = []
    
    user_record = None
    for entry in entries:
        if entry['user'] == user:
            user_record = entry
            break
    
    reward = None
    source = None
    if user_record:
        if achievement_id not in user_record['achievements']:
            user_record['achievements'].append(achievement_id)
            user_db = User.query.filter_by(user=user).first()
            if user_db:
                for a in achievements:
                    if a['id'] == achievement_id:
                        reward = a['reward']
                        source = a['source']
            
                if reward == 'profile_background':
                    backgrounds = json.loads(user_db.unlocked_backgrounds or '[]')
                    if source not in backgrounds:
                        backgrounds.append(source)
                        user_db.unlocked_backgrounds = json.dumps(backgrounds)
                
                if reward == "xp":
                    user_db.xp += int(source)
            
            db.session.commit()


    else:
        entries.append({
            "user": user,
            "achievements": [achievement_id]
        })
        user_db = User.query.filter_by(user=user).first()
        if user_db:
            for a in achievements:
                if a['id'] == achievement_id:
                    reward = a['reward']
                    source = a['source']
        
            if reward == 'profile_background':
                backgrounds = json.loads(user_db.unlocked_backgrounds or '[]')
                if source not in backgrounds:
                    backgrounds.append(source)
                    user_db.unlocked_backgrounds = json.dumps(backgrounds)
        
        db.session.commit()

    
    with open('achievements.json', 'w') as f:
        json.dump(entries, f)
    
def award_flair(user, achievement_id):
    try:
        with open('flairs.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    
    user_record = None
    for entry in entries:
        if entry['user'] == user:
            user_record = entry
            break
    
    if user_record:
        if achievement_id not in user_record['flairs']:
            user_record['flairs'].append(achievement_id)
    else:
        entries.append({
            "user": user,
            "flairs": [achievement_id]
        })
    
    with open('flairs.json', 'w') as f:
        json.dump(entries, f)

def xp_needed(level):
    return round(20 * 1.4 ** level)

def calculate_level(xp_total):
    level = 1
    xp = xp_total
    while xp >= xp_needed(level):
        xp -= xp_needed(level)
        level += 1
    return level,xp, xp_needed(level)