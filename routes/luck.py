from flask import Blueprint, render_template, request, redirect, session
import json
from datetime import datetime
import os
from helpers import award_achievement
import random

luck = Blueprint('luck', __name__)

def spin():
    if len(session['spinsolo']['remaining_numbers']) >= 2:
        chosen_number = random.choice(session['spinsolo']['remaining_numbers'])
        session['spinsolo']['chosen_number'] = chosen_number
        session['spinsolo']['remaining_numbers'].remove(chosen_number)
        session['spinsolo']['round'] += 1
        if 0 <= session['spinsolo']['round'] <= 3:
            session['spinsolo']['multiplier'] = 1
        if 4 <= session['spinsolo']['round'] <= 6:
            session['spinsolo']['multiplier'] = 1.5
        if session['spinsolo']['round'] == 7:
            session['spinsolo']['multiplier'] = 2
        if session['spinsolo']['round'] == 8:
            session['spinsolo']['multiplier'] = 2.5
        if session['spinsolo']['round'] == 9:
            session['spinsolo']['multiplier'] = 3
        if session['spinsolo']['round'] == 10:
            session['spinsolo']['multiplier'] = 4
        if 11 <= session['spinsolo']['round'] <= 13:
            session['spinsolo']['multiplier'] = 5


        session.modified = True
        return chosen_number


@luck.route('/numberspin')
def main():

    try:
        with open('spininfo.json', 'r') as f:
            info = json.load(f)
    except:
        info = []
    list1 = []
    for i in info:
        for score in i['scores']:
            list1.append([i['user'], score])
    list1.sort(key=lambda x: x[1], reverse=True)

    user = session.get('user')
    user_scores = []
    for a in info:
        if user == a['user']:
            user_scores = a['scores']
    user_scores.sort(reverse=True)


    return render_template('numberspin.html', list1=list1, user_scores=user_scores, user=user)

@luck.route('/numberspin/solo')
def solo():
    if 'spinsolo' not in session:
        session['spinsolo'] = {
            "remaining_numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
            "round": 0,
            "multiplier": 1,
            "score": 0,
            "chosen_number": "",
            "buttons": True,
            "state": "playing"
        }
        chosen_number = spin()
    return render_template('spinsolo.html')

@luck.route('/numberspin/solo/higher')
def higher():
    pnumber = session['spinsolo']['chosen_number']
    chosen_number = spin()
    if chosen_number < pnumber:
        session['spinsolo']['score'] = 0
        session['spinsolo']['buttons'] = False
        session['spinsolo']['state'] = 'loss'
        session.modified = True
    else:
        session['spinsolo']['score'] += int(round(session['spinsolo']['multiplier'] * session['spinsolo']['chosen_number']))
        session.modified = True
    return redirect('/numberspin/solo')

@luck.route('/numberspin/solo/lower')
def lower():
    pnumber = session['spinsolo']['chosen_number']
    chosen_number = spin()
    if chosen_number > pnumber:
        session['spinsolo']['score'] = 0
        session['spinsolo']['buttons'] = False
        session['spinsolo']['state'] = 'loss'
        session.modified = True
    else:
        session['spinsolo']['score'] += int(round(session['spinsolo']['multiplier'] * session['spinsolo']['chosen_number']))
        session.modified = True

    return redirect('/numberspin/solo')

@luck.route('/numberspin/solo/end')
def end():
    session['spinsolo']['state'] = 'win'
    session.modified = True
    try:
        with open('spininfo.json', 'r') as f:
            info = json.load(f)
    except FileNotFoundError:
        info = []
    
    user = session.get('user')
    for i in info:
        if i['user'] == user:
            i['scores'].append(session['spinsolo']['score'])
            break
    else:
        new = {
            'user': user,
            'scores': [session['spinsolo']['score']]
        }
        info.append(new)
    
    with open('spininfo.json', 'w') as f:
        json.dump(info, f)
    return redirect('/numberspin/solo')

@luck.route('/spinsolo/test')
def end_session():
    session.pop('spinsolo', None)
    return redirect('/numberspin/solo')

@luck.route('/numberspin/solo/new')
def new_game():
    session.pop('spinsolo', None)

    return redirect('/numberspin/solo')