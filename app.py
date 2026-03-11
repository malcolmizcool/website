import os
from flask import Flask, render_template, request, redirect
import json
from datetime import datetime
app = Flask(__name__)

#this is a test. i want to see what happens!!!!

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return render_template('status.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

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

@app.route('/guest')
def guest():
    try:
        with open('guestbook.json', 'r') as f:
            entries = json.load(f)
    except FileNotFoundError:
        entries = []
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
    
    entry = {
        'name': name,
        'message': comment,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    entries.append(entry)
    with open('guestbook.json', 'w') as f:
        json.dump(entries, f)

    return redirect('/guest')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)