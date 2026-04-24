import os
from flask import Flask, render_template, request, redirect, session

import json
from datetime import datetime, timedelta
from flask_migrate import Migrate
import pytz
import uuid
from flask_sqlalchemy import SQLAlchemy
from pymdownx import emoji
import bleach, markdown
from extensions import db
import sys
from models import Thread, Post


from routes.auth import auth
from routes.blog import blog
from routes.guest import guest
from routes.jack import jack
from routes.admin import admin
from routes.luck import luck
from routes.forum import forum

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

migrate = Migrate(app, db)

app.register_blueprint(auth)
app.register_blueprint(blog)
app.register_blueprint(guest)
app.register_blueprint(jack)
app.register_blueprint(admin)
app.register_blueprint(luck)
app.register_blueprint(forum)

pages = ["empty", 
         "faqs", 
         "report",
         "status",
         "thanks",
         "newpost"]


@app.route('/<page>')
def catch(page):
    if page in pages:
        return render_template(page + '.html')
    return "404 not found", 404

@app.template_filter('md')
def markdown_filter(text):
    return markdown.markdown(text, extensions=[
    # built-in extensions
    'tables',               # | table | syntax |
    'fenced_code',          # ``` code blocks ```
    'attr_list',            # add attributes to elements
    'def_list',             # definition lists
    'footnotes',            # footnote[^1] syntax
    'abbr',                 # abbreviations
    'admonition',           # !!! note "title" blocks
    'toc',                  # [TOC] table of contents
    'sane_lists',           # better list behaviour
    'smarty',               # smart quotes and dashes

    # pymdownx extensions
    'pymdownx.mark',        # ==highlight==
    'pymdownx.tilde',       # ~~strikethrough~~
    'pymdownx.caret',       # ^^underline^^ and ^superscript^
    'pymdownx.emoji',       # :smile:
    'pymdownx.tasklist',    # - [ ] checkboxes
    'pymdownx.superfences', # better code blocks
    'pymdownx.highlight',   # syntax highlighting in code blocks
    'pymdownx.inlinehilite',# `#!python inline code` highlighting
    'pymdownx.keys',        # ++ctrl+c++ keyboard keys
    'pymdownx.details',     # ??? collapsible blocks
    'pymdownx.tabbed',      # === tabbed content
    'pymdownx.smartsymbols',# (tm) (c) (r) symbols
    'pymdownx.magiclink',   # auto-links URLs without []()
    'pymdownx.betterem',    # smarter bold/italic handling
    'pymdownx.critic',      # {--delete--} {++add++} markup
    'pymdownx.snippets',    # --8<-- include files
    'pymdownx.progressbar',
    
], extension_configs={
    'pymdownx.tasklist': {
        'custom_checkbox': True,
    },
    'pymdownx.tabbed': {
        'alternate_style': True,  # required for modern tab syntax
    },
    'pymdownx.arithmatex': {
        'generic': True,
    },
})

def render_md(text):
    html = markdown.markdown(text)
    allowed_tags = ['p','strong','em','ul','ol','li','code','pre','blockquote','h3','h4','a', 'highlight']
    return bleach.clean(html, tags=allowed_tags, strip=True)

@app.before_request
def update_last_seen():
    if request.path.startswith('/static'):
        return  
    if session.get('user'):
        with open('uandp.json', 'r') as f:
            users = json.load(f)
        for user in users:
            if user['username'] == session['user']:
                tz = pytz.timezone('Australia/Sydney')
                user['lastSeen'] = datetime.now(tz).strftime('%d/%m/%y %H:%M:%S')
                break
        with open('uandp.json', 'w') as f:
            json.dump(users, f)

@app.route('/')
def index():

    tz = pytz.timezone('Australia/Sydney')
    now = datetime.now(tz)
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    
    excluded = ['admin', 'guest']

    online_users = []
    new_users = []
    all_users = []

    for user in users:
        last_seen = tz.localize(datetime.strptime(user['lastSeen'], '%d/%m/%y %H:%M:%S'))
        online = now - last_seen < timedelta(minutes=5)
        all_users.append(user['username'])
        if online:
            online_users.append(user['username'])

    new_users = sorted(users, key=lambda u: datetime.strptime(u['accountDate'], '%d/%m/%y'), reverse=True)
    new_users = [[u['username'], u['accountDate']] for u in new_users[:5]]

    tonline_users = len(online_users)
    online_users = online_users[:5]

    all_users_sorted = sorted(
    [u for u in users if u['username'] not in excluded],
    key=lambda u: datetime.strptime(u['lastSeen'], '%d/%m/%y %H:%M:%S'),
    reverse=True
)

    active_users = []
    for user in all_users_sorted[:5]:
        last_seen = tz.localize(datetime.strptime(user['lastSeen'], '%d/%m/%y %H:%M:%S'))
        diff = now - last_seen
        if diff < timedelta(minutes=5):
            status = 'online'
        elif diff < timedelta(hours=1):
            minutes = int(diff.total_seconds() // 60)
            status = f'{minutes}m ago'
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() // 3600)
            status = f'{hours}h ago'
        elif diff < timedelta(days=30):
            days = diff.days
            status = f'{days}d ago'
        else:
            years = int(diff.total_seconds() //  (3.154 * 10 ** 7))
            status = f'{years}y ago'
            
        active_users.append({'username': user['username'], 'status': status})

    FEATURED_THREAD_ID = 6

    featured = Post.query.filter_by(thread_id=FEATURED_THREAD_ID).order_by(Post.created_at.asc()).first()
    featured_thread = Thread.query.get(FEATURED_THREAD_ID)

    try:
        with open('counter.json', 'r') as f:
            counter = json.load(f)
        visit_counter = int(counter['landing_page']) + 1
        counter['landing_page'] = str(visit_counter)
    except FileNotFoundError:
        counter = {'landing_page': 300}
        visit_counter = 300
    except:
        counter = {'landing_page': "error"}
        visit_counter = 'error'
    


    with open('counter.json', 'w') as f:
        json.dump(counter, f)

    counted_users = len(all_users)


    with open('feedback.json', 'r') as f:
        feedback = json.load(f)
    
    nfeedback = len(feedback)

    total_blackjack_wins = 0
    total_numberspin_points = 0
    with open('playergameinfo.json', 'r') as f:
        game_info = json.load(f)
    
    with open('spininfo.json', 'r') as f:
        spin_info = json.load(f)
    
    
    for entry in game_info:
        total_blackjack_wins += int(entry['bswins'])
    
    for entry in spin_info:
        user_spin_points = 0
        for score in entry['scores']:
            user_spin_points += score
        total_numberspin_points += user_spin_points


    return render_template('newindex.html', online_users=online_users, new_users=new_users, featured=featured, featured_thread=featured_thread, tonline_users=tonline_users, counter=visit_counter, counted_users=counted_users,
                           nfeedback=nfeedback,
                           active_users=active_users,
                           total_blackjack_wins=total_blackjack_wins, total_numberspin_points=total_numberspin_points)

@app.route('/oldpage')
def old_page():

    return render_template('index.html')

@app.route('/games')
def games():
    try:
        with open('playergameinfo.json', 'r') as f:
            playerinfo = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        playerinfo = []

    if session.get('user'):
        if not any(p['user'] == session['user'] for p in playerinfo):
            player = {
                'user': session['user'],
                'brating': 1000,
                'bswins': 0,
                'bmwins': 0,
                'tblackjacks': 0
            }
            playerinfo.append(player)
            with open('playergameinfo.json', 'w') as f:
                json.dump(playerinfo, f)

    return render_template('games.html')


@app.route('/reportSubmit', methods=['POST'])
def reportSubmit():

    name = request.form['name']
    feedback = request.form['message']
    aname = session.get('user')
    try:
        with open('feedback.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    tz = pytz.timezone('Australia/Melbourne')
    entry = {
        'name': name,
        'feedback': feedback,
        'date': datetime.now(tz).strftime('%d/%m/%y %H:%M'),
        'actualname': aname
    }
    if not name or not feedback:
        return redirect('/reportSubmit')
    entries.append(entry)
    with open('feedback.json', 'w') as f:
        json.dump(entries, f)
    ctime = datetime.now().isoformat()
    with open('notifications.json', 'r') as f:
        notifications = json.load(f)
    new_notification = {
        'id': str(uuid.uuid4()),
        'title': 'New feedback',
        'message': f'A new ticket has been opened in feedback from user {aname} regarding {name}',
        'time': ctime,
        'is_read': False,
        'type': None
    }
    for entry in notifications:
        if entry['user'] == 'malcolm':
            entry['notifications'].append(new_notification)
    with open('notifications.json', 'w') as f:
        json.dump(notifications, f)
    return render_template('thanks.html')

@app.template_filter('format_time')
def format_time(value):
    dt = datetime.fromisoformat(value)
    return dt.strftime('%d %B %Y, %I:%M %p')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)