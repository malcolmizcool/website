import json

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

def award_achievement(user, achievement_id):
    try:
        with open('achievements.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    
    user_record = None
    for entry in entries:
        if entry['user'] == user:
            user_record = entry
            break
    
    if user_record:
        if achievement_id not in user_record['achievements']:
            user_record['achievements'].append(achievement_id)
    else:
        entries.append({
            "user": user,
            "achievements": [achievement_id]
        })
    
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