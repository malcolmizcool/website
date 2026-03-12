import os
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json
from datetime import datetime
import pytz
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')


pages = ["empty", 
         "faqs", 
         "games",
         "report",
         "status",
         "thanks"]

@app.route('/<page>')
def catch(page):
    if page in pages:
        return render_template(page + '.html')
    return "404 not found", 404


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/blog')
def blog():
    try:
        with open('blog.json', 'r') as f:
            blogs = json.load(f)
    except FileNotFoundError:
        return "error"
    blogs.reverse()
    return render_template('blog.html', blogs=blogs)

@app.route('/blog/<id>')
def blogpost(id):
    try:
        with open('blog.json', 'r') as f:
            blogs = json.load(f)
    except FileNotFoundError:
        return "error"
    post = next((p for p in blogs if p['id'] == id), None)
    return render_template('blogpost.html', post=post)

@app.route('/guest')
def guest():
    try:
        with open('guestbook.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    entries.reverse()
    return render_template('guest.html', entries=entries)

@app.route('/process', methods=['POST'])
def process():
    name = request.form['name']
    comment = request.form['message']
    try:
        with open('guestbook.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    tz = pytz.timezone('Australia/Melbourne')
    entry = {
        'name': name,
        'message': comment,
        'date': datetime.now(tz).strftime('%d/%m/%y %H:%M')
    }
    if not name or not comment:
        return redirect('/sign')
    entries.append(entry)
    with open('guestbook.json', 'w') as f:
        json.dump(entries, f)

    return redirect('/guest')

@app.route('/reportSubmit', methods=['POST'])
def reportSubmit():

    name = request.form['name']
    feedback = request.form['message']
    try:
        with open('feedback.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
    tz = pytz.timezone('Australia/Melbourne')
    entry = {
        'name': name,
        'feedback': feedback,
        'date': datetime.now(tz).strftime('%d/%m/%y %H:%M')
    }
    if not name or not feedback:
        return redirect('/reportSubmit')
    entries.append(entry)
    with open('feedback.json', 'w') as f:
        json.dump(entries, f)
    return render_template('thanks.html')

@app.route('/register')
def register():
    return render_template('register.html')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/createAccount', methods=['POST'])
def createAccount():
    username = request.form['username']
    password = request.form['password']
    try:
        with open('uandp.json', 'r') as f:
            details = json.load(f)
            for detail in details:
                if username == detail['username']:
                    return f"error <br> <a href={"/"}><button style={"cursor: pointer"}>Go Home</button></a>"
    except FileNotFoundError:
        details = []
    
    detail = {
        'username': username,
        'password': generate_password_hash(password)
    }

    if not username or not password:
        return f"error <br> <a href={"/"}>Go Home</a>"
    details.append(detail)
    with open('uandp.json', 'w') as f:
        json.dump(details, f)
    return "account created"

@app.route('/loginAccount', methods=['POST'])
def loginAccount():
    username = request.form['username']
    password = request.form['password']
    try:
        with open('uandp.json', 'r') as f:
            details = json.load(f)
            for detail in details:
                if username == detail['username'] and check_password_hash(detail['password'], password):
                    session['user'] = username
                    return redirect('/')
            return f"error <br> <a href={"/"}>Go Home</a>"
    except FileNotFoundError:
        return f"error <br> <a href={"/"}>Go Home</a>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)