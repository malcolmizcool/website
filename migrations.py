from app import app
from extensions import db
from models import User
import json

with app.app_context():
    db.create_all()
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
    print(f"{updated_users} users successfully migrated")