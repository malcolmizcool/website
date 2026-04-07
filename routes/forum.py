from flask import Blueprint, render_template, request, redirect, session
from extensions import db
from models import Thread, Post
import json
from datetime import datetime, timedelta

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
    
    return redirect(f'/forum/{board}/{thread_id}')