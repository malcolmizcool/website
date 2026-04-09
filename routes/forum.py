from flask import Blueprint, render_template, request, redirect, session
from extensions import db
from models import Thread, Post
import json
from datetime import datetime, timedelta
import uuid

forum = Blueprint('forum', __name__)

BOARDS = {
    'announcements': {'name': 'Announcements', 'description': 'Site updates and news', 'restricted': True},
    'general': {'name': 'General', 'description': 'General discourse', 'restricted': False},
    'games': {'name': 'Games', 'description': 'Regarding games', 'restricted': False},
    'feedback': {'name': 'Feedback', 'description': 'Suggestions and ideas for the future of this site', 'restricted': False},
}

@forum.route('/forum')
def forum_index():

    boards = []
    for slug, info in BOARDS.items():
        thread_count = Thread.query.filter_by(board=slug).count()
        latest = Thread.query.filter_by(board=slug).order_by(Thread.created_at.desc()).first()
        boards.append({
            'slug': slug,
            'name': info['name'],
            'description': info['description'],
            'thread_count': thread_count,
            'latest': latest
        })
    return render_template('forum/home.html', boards=boards)

@forum.route('/forum/<board>', strict_slashes=False)
def board_page(board):
    if board not in BOARDS:
        return "404 not found", 404
    threads = Thread.query.filter_by(board=board).order_by(Thread.is_pinned.desc(), Thread.created_at.desc()).all()
    roles = {}
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    for user in users:
        role = user['role'] 
        roles[user['username']] = role
    return render_template('forum/board.html', threads=threads, board=BOARDS[board], slug=board, roles=roles)

@forum.route('/forum/<board>/new', strict_slashes=False)
def new_thread(board):
    if board not in BOARDS:
        return "404 not found", 404
    if not session.get('user'):
        return redirect('/login')
    if BOARDS[board]['restricted'] and session.get('user') != 'malcolm':
        return "not authorised", 403
    return render_template('forum/new_thread.html', board=BOARDS[board], slug=board)

@forum.route('/forum/<board>/new', methods=['POST'], strict_slashes=False)
def create_thread(board):
    if board not in BOARDS:
        return "404 not found", 404
    if not session.get('user'):
        return redirect('/login')
    if BOARDS[board]['restricted'] and session.get('user') != 'malcolm':
        return "not authorised", 403
    
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not title or not content:
        return redirect(f'/forum/{board}/new')
    
    thread = Thread(
        title=title,
        board=board,
        author=session['user']
    )
    db.session.add(thread)
    db.session.flush() 
    
    post = Post(
        thread_id=thread.id,
        author=session['user'],
        content=content
    )
    db.session.add(post)
    db.session.commit()
    
    return redirect(f'/forum/{board}/{thread.id}')

@forum.route('/forum/<board>/<int:thread_id>', strict_slashes=False)
def thread_page(board, thread_id):
    if board not in BOARDS:
        return "404 not found", 404
    thread = Thread.query.get(thread_id)
    if not thread:
        return "404 not found", 404
    posts = Post.query.filter_by(thread_id=thread_id).order_by(Post.created_at.asc()).all()
    roles = {}
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    for user in users:
        role = user['role'] 
        roles[user['username']] = role
    online_status = {}
    for user in users:
        last_online = datetime.strptime(user['lastSeen'], "%d/%m/%y %H:%M:%S")
        status = datetime.now() - last_online < timedelta(minutes=5)
        online_status[user['username']] = status
    return render_template('forum/thread.html', thread=thread, posts=posts, board=BOARDS[board], slug=board, roles=roles, online_status=online_status)

@forum.route('/forum/<board>/<int:thread_id>/reply', methods=['POST'], strict_slashes=False)
def reply(board, thread_id):
    if not session.get('user'):
        return redirect('/login')
    
    thread = Thread.query.get(thread_id)
    thread_author = thread.author
    thread_title = thread.title
    if not thread or thread.is_locked:
        return "404 not found", 404
    
    content = request.form.get('content')
    if not content:
        return redirect(f'/forum/{board}/{thread_id}')
    
    post = Post(
        thread_id=thread_id,
        author=session['user'],
        content=content
    )
    db.session.add(post)
    db.session.commit()

    time = datetime.now().isoformat()

    with open ('notifications.json', 'r') as f:
        notification_entries = json.load(f)
    

    for entry in notification_entries:
        if entry['user'] == thread_author and thread_author != session['user']:
            new_notification = {
            'id': str(uuid.uuid4()),
            'title': 'New reply',
            'message': session['user'] + " has replied to your post '" + thread_title + "'",
            'time': time,
            'is_read': False,
            'type': None
            }

            entry['notifications'].append(new_notification)
    with open('notifications.json', 'w') as f:
        json.dump(notification_entries, f)
    

    
    return redirect(f'/forum/{board}/{thread_id}')

@forum.route('/forum/post/delete', methods=['POST'])
def delete_post():
    if not session.get('user'):
        return redirect('/login')
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    roles = {user['username']: user['role'] for user in users}
    if roles.get(session['user'], 'user') != 'admin':
        return "not authorised", 403
    
    post_id = request.form.get('post_id')
    thread_id = request.form.get('thread_id')
    board = request.form.get('board')
    
    post = Post.query.get(post_id)
    if not post:
        return "404 not found", 404
    
    db.session.delete(post)
    db.session.commit()
    
    return redirect(f'/forum/{board}/{thread_id}')

@forum.route('/forum/thread/delete', methods=['POST'])
def delete_thread():
    if not session.get('user'):
        return redirect('/login')
    with open('uandp.json', 'r') as f:
        users = json.load(f)
    roles = {user['username']: user['role'] for user in users}
    if roles.get(session['user'], 'user') != 'admin':
        return "not authorised", 403
    
    thread_id = request.form.get('thread_id')
    board = request.form.get('board')
    
    thread = Thread.query.get(thread_id)
    if not thread:
        return "404 not found", 404
    
    Post.query.filter_by(thread_id=thread_id).delete()
    db.session.delete(thread)
    db.session.commit()
    
    return redirect(f'/forum/{board}')