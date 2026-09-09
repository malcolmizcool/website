from flask import Blueprint, render_template, request, redirect, session
import json
import random
from helpers import load_json, award_achievement, data_path
from models import User

suit_names = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
value_names = {'J': 'Jack', 'Q': 'Queen', 'K': 'King', 'A': 'Ace'}
def format_card(card):
    value = card[:-1]
    suit = card[-1]
    value = value_names.get(value, value)
    suit = suit_names.get(suit, suit)
    return f"{value} {suit}"

def update_player_stats(username, updates):
    players = load_json('playergameinfo.json', [])
    for player in players:
        if player['user'] == username:
            for key, value in updates.items():
                player[key] = value
            break
    with open(data_path('playergameinfo.json'), 'w') as f:
        json.dump(players, f)

def dealer_play(game):
    while calculate_hand(game['dealer_hand']) < 17:
        game['dealer_hand'].append(game['deck'].pop())
    return game

def calculate_hand(hand):
    total = 0
    aces = 0
    
    for card in hand:
        value = card[:-1]
        if value in ['J', 'Q', 'K']:
            total += 10
        elif value == 'A':
            total += 11
            aces += 1
        else:
            total += int(value)
    
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    
    return total

jack = Blueprint('jack', __name__)

@jack.route("/blackjack")
def blackjack():
    info = load_json('playergameinfo.json', [])
    db_users = User.query.all()

    plist = {}
    for p in db_users:
            plist[p.user] = p.role or 'user'


    player = next((p for p in info if p['user'] == session.get('user')), None)
    leaderboard_wins = sorted(info, key=lambda p: p['bswins'], reverse=True)[:3]
    leaderboard_blackjacks = sorted(info, key=lambda p: p['tblackjacks'], reverse=True)[:3]

    return render_template('games/blackjack.html', player=player, info=info, leaderboard_blackjacks=leaderboard_blackjacks, leaderboard_wins=leaderboard_wins, players=plist)

@jack.route("/blackjack/solo")
def singlejack():
    bjack = False
    if 'blackjacksolo' not in session:
        suits = ['H', 'D', 'C', 'S']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        deck = [v + s for v in values for s in suits]
        random.shuffle(deck)

        game = {
            'deck': deck,
            'hand': [],
            'dealer_hand': [],
            'status': 'playing',
            'win': None
        }

        game['hand'].extend([game['deck'].pop(), game['deck'].pop()])
        game['dealer_hand'].extend([game['deck'].pop(), game['deck'].pop()])
        session['blackjacksolo'] = game
        if calculate_hand(game['hand']) == 21 and len(game['hand']) == 2:
            players = load_json('playergameinfo.json', [])
            if session.get('user'):
                for player in players:
                    if player['user'] == session['user']:
                        player['tblackjacks'] += 1
                        break
            with open(data_path('playergameinfo.json'), 'w') as f:
                json.dump(players, f)
        session['blackjacksolo'] = game
    else:
        game = session['blackjacksolo']
    




    counted_hand = calculate_hand(game['hand'])
    if counted_hand == 21  and len(game['hand']) == 2:
        bjack = True

        if session.get('user'):
            player_achievements = load_json('achievements.json', [])
            game_info = load_json('playergameinfo.json', [])
            for entry in game_info:
                if entry['user'] == session.get('user'):
                    if entry['tblackjacks'] == 21:
                        award_achievement(session['user'], '21_blackjack')



    formatted_hand = [format_card(c) for c in game['hand']]
    formatted_dealer = [format_card(c) for c in game['dealer_hand']]

    return render_template('games/blackjacksolo.html', game=game, hand=formatted_hand, dealer=formatted_dealer, bjack=bjack)

@jack.route("/blackjack/hit")
def hit():
    game = session['blackjacksolo']
    game['hand'].append(game['deck'].pop())
    session['blackjacksolo'] = game


    if calculate_hand(game['hand']) > 21:
        game['win'] = 'bust'
        game['status'] = 'end'
        session['blackjacksolo'] = game


    return redirect("/blackjack/solo")

@jack.route("/blackjack/end")
def stand():
    game = session['blackjacksolo']
    game['status'] = 'end'
    session['blackjacksolo'] = game

    if game['win'] is None:
        game = dealer_play(game)
        

    if calculate_hand(game['dealer_hand']) < calculate_hand(game['hand']) <= 21:
        game['win'] = True
        players = load_json('playergameinfo.json', [])
        if session.get('user'):
            for player in players:
                if player['user'] == session['user']:
                    player['bswins'] += 1
                    if player['bswins'] == 100:
                        award_achievement(session['user'], 'bj_100_wins')
                    break
        with open(data_path('playergameinfo.json'), 'w') as f:
            json.dump(players, f)

    
    if 21 >= calculate_hand(game['dealer_hand']) > calculate_hand(game['hand']):
        game['win'] = False
    
    if calculate_hand(game['dealer_hand']) > 21 and game['win'] != False:
        game['win'] = True
        players = load_json('playergameinfo.json', [])
        if session.get('user'):
            for player in players:
                if player['user'] == session['user']:
                    player['bswins'] += 1
                    if player['bswins'] == 100:
                        award_achievement(session['user'], 'bj_100_wins')
                    break
        with open(data_path('playergameinfo.json'), 'w') as f:
            json.dump(players, f)

    if calculate_hand(game['dealer_hand']) == calculate_hand(game['hand']):
        game['win'] = 'draw'


    session['blackjacksolo'] = game

    return redirect("/blackjack/solo")

@jack.route("/blackjack/reset")
def reset():
    session.pop('blackjacksolo', None)
    return redirect("/blackjack/solo")