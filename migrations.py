from app import app
from extensions import db
from models import User
import json

with app.app_context():
    db.create_all()
    upgrade_feedback = []
    updated_users = 0

    with open('uandp.json', 'r') as f:
        users = json.load(f)
    
    for u in users:
        existing = User.query.filter_by(user=u['username']).first()
        if not existing:
            new_user = User(user=u['username'], number_of_pokes=0)
            db.session.add(new_user)
            updated_users += 1
    
    db.session.commit()
    m1 = (f"{updated_users} users successfully migrated")
    upgrade_feedback.append(m1)



    background_users_updated_pickle = 0
    with open('achievements.json', 'r') as f:
        achievements = json.load(f)

    pickles_background_users = []
    for aentry in achievements:
        for userachievements in aentry['achievements']:
            if userachievements == "visit_pickle":
                pickles_background_users.append(aentry['user'])

    for buser in pickles_background_users:
        db_buser = User.query.filter_by(user=buser).first()
        if not db_buser:
            print(f"user not found: {buser}")
            continue
        background_users_updated_pickle += 1
        backgrounds = json.loads(db_buser.unlocked_backgrounds or '[]')
        if 'pickle.png' not in backgrounds:
            backgrounds.append('pickle.png')
        db_buser.unlocked_backgrounds = json.dumps(backgrounds)
    
    db.session.commit()
    m2 = (f"{background_users_updated_pickle} users updated with pickle background")
    upgrade_feedback.append(m2)
  


    for feedback in upgrade_feedback:
        print(feedback)