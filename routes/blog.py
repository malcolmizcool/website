from flask import Blueprint, render_template, request, redirect, session
from datetime import datetime
import json
from helpers import load_json, data_path

blog = Blueprint('blog', __name__)

@blog.route('/blog')
def blog_page():
    try:
        with open(data_path('blog.json'), 'r') as f:
            blogs = json.load(f)
    except FileNotFoundError:
        return "error"
    return render_template('blog/blog.html', blogs=blogs)

@blog.route('/blog/<id>')
def blogpost(id):
    try:
        with open(data_path('blog.json'), 'r') as f:
            blogs = json.load(f)
    except FileNotFoundError:
        return "error"
    post = next((p for p in blogs if p['id'] == id), None)
    return render_template('blog/blogpost.html', post=post)

@blog.route('/createBlogPost', methods=['POST'])
def createBlogPost():
    title = request.form['title']
    message = request.form['message']
    date = request.form['date']
    date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%y')
    try:
        with open(data_path('blog.json'), 'r') as f:
            blogs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        blogs = []
    new_id = str(max(int(b['id']) for b in blogs) + 1) if blogs else '1'
    blogpost = {
        "id": new_id,
        "title": title,
        "content": message,
        "date": date
    }
    blogs.insert(0, blogpost)
    with open ('blog.json', 'w') as f:
        json.dump(blogs, f)
    return redirect('/blog')

@blog.route('/deleteBlogPost', methods=['POST'])
def deleteBlogPost():
        blogid = request.form['id']
        blogs = load_json('blog.json', [])
        blogs = [b for b in blogs if b['id'] != blogid]
        with open(data_path('blog.json'), 'w') as f:
            json.dump(blogs, f)
        return redirect('/blog')

