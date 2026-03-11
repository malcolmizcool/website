import os
from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
import pytz
app = Flask(__name__)

#this is a test. i want to see what happens!!!!

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/empty')
def empty():
    return render_template('empty.html')

@app.route('/faqs')
def faqs():
    return render_template('faqs.html')

@app.route('/games')
def games():
    return render_template('games.html')

@app.route('/sign')
def sign():
    return render_template('sign.html')


@app.route('/report')
def report():
    return render_template('report.html')


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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)