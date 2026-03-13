import os
from flask import Flask, render_template, request, redirect

import json
from datetime import datetime
import pytz

from routes.auth import auth
from routes.blog import blog
from routes.guest import guest

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')


pages = ["empty", 
         "faqs", 
         "games",
         "report",
         "status",
         "thanks",
         "newpost"]

app.register_blueprint(auth)
app.register_blueprint(blog)
app.register_blueprint(guest)

@app.route('/<page>')
def catch(page):
    if page in pages:
        return render_template(page + '.html')
    return "404 not found", 404


@app.route('/')
def index():
    return render_template('index.html')


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