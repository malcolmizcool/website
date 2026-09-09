"""
One-time migration: copies all data from uandp.json into the User database table.

Run this ONCE on the server, after pulling the code update and running
`flask db upgrade` (to add the new columns), and BEFORE removing uandp.json.

Usage:
    python migrate_uandp_to_db.py
"""
import json
from app import app
from extensions import db
from models import User
from helpers import data_path

with app.app_context():
    with open(data_path('uandp.json'), 'r') as f:
        users = json.load(f)

    created = 0
    updated = 0

    for u in users:
        existing = User.query.filter_by(user=u['username']).first()

        if existing is None:
            existing = User(user=u['username'], number_of_pokes=0)
            db.session.add(existing)
            created += 1
        else:
            updated += 1

        # Copy every field across, keeping the password hash exactly as-is
        existing.password = u.get('password')
        existing.bio = u.get('bio', '')
        existing.pfp = u.get('pfp', 'None')
        existing.role = u.get('role', 'user')
        existing.accountDate = u.get('accountDate', '')
        existing.verified = str(u.get('verified', 'False')).lower() == 'true'
        existing.lastSeen = u.get('lastSeen', '')

    db.session.commit()

    print(f"Migration complete: {created} users created, {updated} users updated.")
    print(f"Total users in uandp.json: {len(users)}")
    print("Once you've confirmed everything works, you can safely delete uandp.json.")
