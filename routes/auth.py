from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
import json

auth = Blueprint('auth', __name__)

@auth.route('/register')
def register():
    return render_template('register.html')
@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/createAccount', methods=['POST'])
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
    session['user'] = username
    return redirect('/')

@auth.route('/loginAccount', methods=['POST'])
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
    
@auth.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')