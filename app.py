import os
from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)